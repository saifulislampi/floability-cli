import ndcctools.taskvine as vine

class PythonTaskStrace(vine.PythonTask):
    def wrapper_fn(fn, *args, **kwargs):
        import os
        import time
        import traceback
        import subprocess
        import signal

        parent_pid = os.getpid()
        child_pid = os.fork() 

        if child_pid == 0:
            # strace options:
            # -qqq   : Suppress various information (max quiet)
            # -r     : Print relative timestamp for each line
            # -z     : Print only successful system calls
            # -f     : Follow child processes (trace across fork)
            # --trace file : Only trace file-related system calls
            # -p     : Attach to the specified process ID
            os.execlp("strace", "strace", "-qqq", "-r", "-z", "-f", "--trace", "file", "--output", "strace.txt", "-p", str(parent_pid))
            print("Failed to exec strace")  # Only reached if execlp fails
            os._exit(1)
        elif child_pid > 0:
            try:
                time.sleep(1)
                result = fn(*args, **kwargs)

                os.kill(child_pid, signal.SIGTERM)
                s = os.waitpid(child_pid, 0)

                return result
            except Exception as e:
                print(traceback.format_exc())
                os._exit(1)
        else:
            # Parent process could not fork
            print(traceback.format_exc())
            os._exit(1)

        return result



    def __init__(self, *args, strace_file=None, **kwargs):
        if strace_file is None or not isinstance(strace_file, vine.File):
            raise ValueError("strace_file must be provided, and must be a vine.File object")

        fn = args[0]
        args = args[1:]

        super().__init__(PythonTaskStrace.wrapper_fn, fn, *args, **kwargs)

        self.add_output(strace_file, "strace.txt")



def test_fn(*args, **kwargs):
    import random
    s = "Hello, World!. args: {}, kwargs: {}".format(args, kwargs)
    s += f"\n {random.randint(0, 1000000)=}"

    with open("/etc/motd", "r") as f:
        lines = f"\n {f.read()}"

    return s

if __name__ == "__main__":

    port = 9123

    m = vine.Manager(port=port)

    f = m.declare_file("strace.txt")
    t = PythonTaskStrace(test_fn, 1, 2, 3, a=4, b=5, strace_file=f)

    m.submit(t)

    workers = vine.Factory(manager=m)
    workers.max_workers = 1
    workers.min_workers = 1
    workers.cores = 1
    workers.memory = 1000
    workers.disk = 1000

    with workers:
        t = m.wait(5)
        if t:
            print(f"Task completed. Result: {t.result}. Exit code: {t.exit_code}\n Output: {t.output}")
            print("First 40 lines of strace output:")
            with open('strace.txt', 'r') as f:
                for line in f.readlines()[:40]:
                    print(line.strip())

