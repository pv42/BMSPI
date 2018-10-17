def read_file(name):
    fh = open("www/" + name, "r")
    fc = fh.read()
    fh.close()
    return fc


def create_login(failed):
    if failed:
        failed_str = "password or username wrong<br/>"
    else:
        failed_str = ""
    return read_file("head.html").format("login") + "<body>" + read_file("login.html").format(failed_str) + "</body" \
                                                                                                            "></html> "


def create_data_overview(voltages, data_config):
    return read_file("overview_data.html").format(voltages, data_config)


def create_email_overview(email_state):
    if email_state["enabled"]:
        email_str = "enabled, sending to {}".format(email_state["receiver"])
    else:
        email_str = "disabled"
    return read_file("overview_email.html").format(email_str)


def create_stopping():
    return "<div id='stopping'>BMS is stopping ...</div>"


def create_starting():
    return "<div id='stopping'>BMS is starting ...</div>"


def create_bms_overview(bms):
    if bms.is_running:
        if bms.should_run:
            content = create_stop()
        else:
            content = create_stopping()
    else:
        if bms.should_run:
            content = create_starting()
        else:
            content = create_start()
    return "<div id=''><h1>BMS</h1>" + "Version: " + bms.version + content + "</div>"


def create_start():
    return "<div id='start'>BMS is stopped. <a href='start'>Start it</a></div>"


def create_stop():
    return "<div id='stop'>BMS is running. <a href='stop'>Stop it</a></div>"


def create_main(voltages, email_config, data_config, bms):
    return create_header("Home") + "<body>" + create_data_overview(voltages, data_config) + \
           create_email_overview(email_config) + create_bms_overview(bms) + \
           "</body></html>"


def create_email(email_config):
    checked_str = ""
    if email_config["enabled"]:
        checked_str = "checked"
    return create_header("email") + "<body>" + read_file("email.html").format(checked_str, email_config) + "</body" \
                                                                                                           "></html> "


def create_header(title):
    return read_file("head.html").format(title)


def create404():
    return create_header("404") + "<body>" + "404 (Not Found) - The requested page was not found" + "</body></html>"


def create403():
    return create_header(
        "403") + "<body>" + "403 (Forbidden) - You are not allowed to view this page<br/>" +\
        "<a href='..'>Log in</a></body></html>"


def create_redirect(url):
    return """<html><head><title>redirecting to {0}</title>
<meta http-equiv="refresh" content="0; URL={0}">
</head>
<body>redirecting to <a href="{0}">{0}</a></p>
</body>
</html>""".format(url)
