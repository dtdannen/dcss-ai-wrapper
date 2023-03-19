def _start_process(self):
    self.socketpath = os.path.join(self.config_path("socket_path"),
                                   self.username + ":" +
                                   self.formatted_time + ".sock")

    try:  # Unlink if necessary
        os.unlink(self.socketpath)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

    game = self.game_params

    call = self._base_call() + ["-webtiles-socket", self.socketpath,
                                "-await-connection"]

    ttyrec_path = self.config_path("ttyrec_path")
    if ttyrec_path:
        self.ttyrec_filename = os.path.join(ttyrec_path, self.lock_basename)

    processes[os.path.abspath(self.socketpath)] = self

    if config.get('dgl_mode'):
        self.logger.info("Starting %s.", game["id"])
    else:
        self.logger.info("Starting game.")

    try:
        self.process = TerminalRecorder(call, self.ttyrec_filename,
                                        self._ttyrec_id_header(),
                                        self.logger,
                                        config.get('recording_term_size'),
                                        env_vars=game.get("env", {}),
                                        game_cwd=game.get("cwd", None), )
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

def connect(self, socketpath, primary = False):
    self.socketpath = socketpath
    self.conn = WebtilesSocketConnection(self.socketpath, self.logger)
    self.conn.message_callback = self._on_socket_message
    self.conn.close_callback = self._on_socket_close
    self.conn.connect(primary)