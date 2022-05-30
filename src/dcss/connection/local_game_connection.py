import os
import sys
import errno
from dcss.connection.config import LocalConfig


class GameConnectionLocal:

    def __init__(self):
        self.socket_path = "/home/dustin/Projects/crawl/crawl-ref/source/rcs/midca:test.sock"
        self.call = ["./home/dustin/Projects/crawl/crawl-ref/source/crawl",
                     "-name",   LocalConfig.agent_name,
                     "-rc", LocalConfig.rc,
                     "-macro",  LocalConfig.macro,
                     "-morgue", LocalConfig.morgue,
                     "-webtiles-socket", self.socketpath,
                     "-await-connection"]

    def _start_process(self):
        try:  # Unlink if necessary
            os.unlink(self.socketpath)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

            self.errpipe_read, errpipe_write = os.pipe()

            self.pid, self.child_fd = pty.fork()

            if self.pid == 0:
                # We're the child
                def handle_signal(signal, f):
                    sys.exit(0)

                signal.signal(1, handle_signal)

                # Set window size
                cols, lines = self.get_terminal_size()
                s = struct.pack("HHHH", lines, cols, 0, 0)
                fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, s)

                os.close(self.errpipe_read)
                os.dup2(errpipe_write, 2)

                # Make sure not to retain any files from the parent
                max_fd = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
                for i in range(3, max_fd):
                    try:
                        os.close(i)
                    except OSError:
                        pass

                # And exec
                env = dict(os.environ)
                env.update(self.env_vars)
                env["COLUMNS"] = str(cols)
                env["LINES"] = str(lines)
                env["TERM"] = "linux"
                if self.game_cwd:
                    os.chdir(self.game_cwd)
                try:
                    os.execvpe(self.command[0], self.command, env)
                except OSError:
                    sys.exit(1)

            # We're the parent
            os.close(errpipe_write)

            IOLoop.current().add_handler(self.child_fd,
                                         self._handle_read,
                                         IOLoop.ERROR | IOLoop.READ)

            IOLoop.current().add_handler(self.errpipe_read,
                                         self._handle_err_read,
                                         IOLoop.READ)

        #
        #
        # ttyrec_path = self.config_path("ttyrec_path")
        # if ttyrec_path:
        #     self.ttyrec_filename = os.path.join(ttyrec_path, self.lock_basename)
        #
        # processes[os.path.abspath(self.socketpath)] = self
        #
        # if config.get('dgl_mode'):
        #     self.logger.info("Starting %s.", game["id"])
        # else:
        #     self.logger.info("Starting game.")
        #
        # try:
        #     self.process = TerminalRecorder(call, self.ttyrec_filename,
        #                                     self._ttyrec_id_header(),
        #                                     self.logger,
        #                                     config.get('recording_term_size'),
        #                                     env_vars=game.get("env", {}),
        #                                     game_cwd=game.get("cwd", None), )
            self.process.end_callback = self._on_process_end
            self.process.output_callback = self._on_process_output
            self.process.activity_callback = self.note_activity
            self.process.error_callback = self._on_process_error

            self.gen_inprogress_lock()

            self.connect(self.socketpath, True)

            self.logger.debug("Crawl FDs: fd%s, fd%s.",
                              self.process.child_fd,
                              self.process.errpipe_read)

            self.last_activity_time = time.time()

            self.check_where()
        except Exception:
            self.logger.warning("Error while starting the Crawl process!", exc_info=True)
            self.exit_reason = "error"
            self.exit_message = "Error while starting the Crawl process!\nSomething has gone very wrong; please let a server admin know."
            self.exit_dump_url = None

            if self.process:
                self.stop()
            else:
                self._on_process_end()

    def _spawn(self):
        self.errpipe_read, errpipe_write = os.pipe()

        self.pid, self.child_fd = pty.fork()

        if self.pid == 0:
            # We're the child
            def handle_signal(signal, f):
                sys.exit(0)
            signal.signal(1, handle_signal)

            # Set window size
            cols, lines = self.get_terminal_size()
            s = struct.pack("HHHH", lines, cols, 0, 0)
            fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSWINSZ, s)

            os.close(self.errpipe_read)
            os.dup2(errpipe_write, 2)

            # Make sure not to retain any files from the parent
            max_fd = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
            for i in range(3, max_fd):
                try:
                    os.close(i)
                except OSError:
                    pass

            # And exec
            env            = dict(os.environ)
            env.update(self.env_vars)
            env["COLUMNS"] = str(cols)
            env["LINES"]   = str(lines)
            env["TERM"]    = "linux"
            if self.game_cwd:
                os.chdir(self.game_cwd)
            try:
                os.execvpe(self.command[0], self.command, env)
            except OSError:
                sys.exit(1)

        # We're the parent
        os.close(errpipe_write)

        IOLoop.current().add_handler(self.child_fd,
                                     self._handle_read,
                                     IOLoop.ERROR | IOLoop.READ)

        IOLoop.current().add_handler(self.errpipe_read,
                                     self._handle_err_read,
                                     IOLoop.READ)


    def connect(self, socketpath, primary = False):
        self.socketpath = socketpath
        self.conn = WebtilesSocketConnection(self.socketpath, self.logger)
        self.conn.message_callback = self._on_socket_message
        self.conn.close_callback = self._on_socket_close
        self.conn.connect(primary)