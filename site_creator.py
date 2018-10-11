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
    return read_file("head.html").format("login") + "<body>" + read_file("login.html").format(failed_str) + \
           "</body></html>"


def create_data_overview(voltages):
    return read_file("overview_data.html").format(voltages)


def create_email_overview(email_state):
    if email_state["enabled"]:
        email_str = "enabled, sending to {}".format(email_state["receiver"])
    else:
        email_str = "disabled"
    return read_file("overview_email.html").format(email_str)


def create_main(voltages, email_state):
    return create_header("Home") + "<body>" + create_data_overview(voltages) + create_email_overview(email_state) + \
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
        "403") + "<body>" + "403 (Forbidden) - You are not allowed to view this page" + "</body></html>"


def create_redirect(url):
    return """<html><head><title>redirecting to {0}</title>
<meta http-equiv="refresh" content="0; URL={0}">
</head>
<body>redirecting to <a href="{0}">{0}</a></p>
</body>
</html>""".format(url)
