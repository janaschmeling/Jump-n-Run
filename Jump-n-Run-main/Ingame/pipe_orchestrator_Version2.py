#!/usr/bin/env python3
"""
Pipe Orchestrator - Launch and connect programs via pipes.

Usage:
  python pipe_orchestrator.py --pipeline "prog1 | prog2"
  python pipe_orchestrator.py --tee "producer => consumer1,consumer2"
"""
import argparse
import subprocess
import shlex
import threading
import sys
import signal
import time
from typing import List, Tuple

child_processes = []
stop_event = threading.Event()

def log(*args, **kwargs):
    print("[orchestrator]", *args, **kwargs, file=sys.stderr)

def start_pipeline(cmds: List[str]) -> List[subprocess.Popen]:
    procs = []
    prev_stdout = None
    for i, cmd in enumerate(cmds):
        args = shlex.split(cmd)
        stdin = prev_stdout if prev_stdout is not None else None
        stdout = subprocess.PIPE
        p = subprocess.Popen(args, stdin=stdin, stdout=stdout, stderr=subprocess.PIPE)
        log("Started:", cmd, "pid=", p.pid)
        child_processes.append(p)
        if prev_stdout is not None:
            try:
                prev_stdout.close()
            except Exception:
                pass
        prev_stdout = p.stdout
        procs.append(p)
    return procs

def tee_forwarder(src_proc, dest_procs, stop_on_fail):
    src = src_proc.stdout
    dests = [p.stdin for p in dest_procs]
    try:
        while not stop_event.is_set():
            chunk = src.read(4096)
            if not chunk:
                break
            for d in dests:
                try:
                    d.write(chunk)
                    d.flush()
                except BrokenPipeError:
                    pass
                except Exception:
                    pass
    except Exception as e:
        log("tee_forwarder error:", e)
    finally:
        for d in dests:
            try:
                d.close()
            except Exception:
                pass

def forward_stderr(proc, name):
    try:
        for line in iter(proc.stderr.readline, b''):
            if not line:
                break
            try:
                prefix = f"[{name} pid={proc.pid}] ".encode()
                sys.stderr.buffer.write(prefix + line)
                sys.stderr.flush()
            except Exception:
                pass
    except Exception:
        pass

def monitor_processes(all_procs, stop_on_fail):
    try:
        while not stop_event.is_set():
            alive = [p for p in all_procs if p.poll() is None]
            if not alive:
                break
            for p in list(all_procs):
                rc = p.poll()
                if rc is not None:
                    log("Process exited:", p.pid, "rc=", rc)
                    if stop_on_fail and rc != 0:
                        log("Stopping all")
                        stop_event.set()
                        kill_all()
                        return
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_event.set()
        kill_all()

def kill_all():
    for p in list(child_processes):
        try:
            if p.poll() is None:
                log("Killing pid", p.pid)
                p.terminate()
                try:
                    p.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    p.kill()
        except Exception:
            pass

def run_pipelines(pipeline_specs, tee_specs, stop_on_fail):
    all_procs = []
    for spec in pipeline_specs:
        parts = [p.strip() for p in spec.split('|') if p.strip()]
        if not parts:
            continue
        procs = start_pipeline(parts)
        all_procs.extend(procs)
        for i, p in enumerate(procs):
            name = f"pipeline#{i}"
            t = threading.Thread(target=forward_stderr, args=(p, name), daemon=True)
            t.start()
    for producer, consumers in tee_specs:
        prod_args = shlex.split(producer)
        prod = subprocess.Popen(prod_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        child_processes.append(prod)
        consumer_procs = []
        for c in consumers:
            c_args = shlex.split(c)
            cp = subprocess.Popen(c_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            child_processes.append(cp)
            consumer_procs.append(cp)
            t = threading.Thread(target=forward_stderr, args=(cp, f"consumer"), daemon=True)
            t.start()
        t = threading.Thread(target=forward_stderr, args=(prod, f"producer"), daemon=True)
        t.start()
        t2 = threading.Thread(target=tee_forwarder, args=(prod, consumer_procs, stop_on_fail), daemon=True)
        t2.start()
        all_procs.append(prod)
        all_procs.extend(consumer_procs)
    monitor_processes(all_procs, stop_on_fail)

def parse_tee_spec(spec):
    if '=>' not in spec:
        raise ValueError("tee spec must contain '=>': " + spec)
    left, right = spec.split('=>', 1)
    producer = left.strip()
    consumers = [c.strip() for c in right.split(',') if c.strip()]
    if not producer or not consumers:
        raise ValueError("tee spec must have producer and at least one consumer")
    return producer, consumers

def setup_signal_handlers():
    def _handler(signum, frame):
        log("Signal", signum, "received")
        stop_event.set()
        kill_all()
    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)

def main():
    parser = argparse.ArgumentParser(description="Pipe Orchestrator")
    parser.add_argument('--pipeline', '-p', action='append', default=[], help='Pipeline spec')
    parser.add_argument('--tee', '-t', action='append', default=[], help='Tee spec')
    parser.add_argument('--stop-on-fail', action='store_true', help='Stop all on failure')
    args = parser.parse_args()

    setup_signal_handlers()

    tee_specs = []
    for ts in args.tee:
        tee_specs.append(parse_tee_spec(ts))

    try:
        run_pipelines(args.pipeline, tee_specs, stop_on_fail=args.stop_on_fail)
        log("All processes finished")
    except Exception as e:
        log("Error:", e)
        kill_all()
        sys.exit(1)

if __name__ == '__main__':
    main()