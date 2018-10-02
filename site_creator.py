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
    return read_file("data_overview.html").format(voltages)


def create_main(voltages, email_state):
    return create_header("Home") + "<body>" + create_data_overview(voltages) + "</body></html>"


def create_header(title):
    return read_file("head.html").format(title)


def create404():
    return create_header("404") + "<body>" + "404 (Not Found) - The requested page was not found" + "</body></html>"


def create403():
    return create_header(
        "403") + "<body>" + "403 (Forbidden) - You are not allowed to view this page" + "</body></html>"
