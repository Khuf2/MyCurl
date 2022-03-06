'''
    Theo Novak - 1656602 - tjnovak
    Final Project CSE150 - Basic curl command implementation
'''

'''
    URL Structure from IBM Documentation:
        scheme://host:port/path?query
'''

from socket import *
import sys

'''
    Initial validation and handling of command line arguments
'''
def validate_arguments():
    if len(sys.argv) == 1:
        # No arguments given in command line
        print("Usage: tjnovakMyCurl.py [fullURL] [optional: hostname]")
        sys.exit(1)

    if "https" in sys.argv[1]:
        # HTTPS not supported.
        server_response_line = "HTTPS connections are not supported."
        print(server_response_line)
        csv_write(success_msg, status_code, requested_url, hostname, clientIP, serverIP, clientPort, serverPort, server_response_line)
        terminal_success_message(success_msg, url, status_code)
        sys.exit(1)

    if len(sys.argv[1:]) > 2:
        # Too many arguments in the command line
        server_response_line = "Too many arguments provided in the command line."
        print(server_response_line)
        csv_write(success_msg, status_code, requested_url, hostname, clientIP, serverIP, clientPort, serverPort, server_response_line)
        terminal_success_message(success_msg, url, status_code)
        sys.exit(1)

def csv_write(success_msg, status_code, requested_url, hostname, clientIP, serverIP, clientPort, serverPort, server_response_line):
    with open('Log.csv', mode='a+') as log_file:
        log_file.seek(0, 2)
        if log_file.tell() == 0:
            log_file.write("Successful or Unsuccessful, Server Status Code, Requested URL, hostname, source IP, destination IP, source port, destination port, Server Response line (including code and phrase)\n")
        csv_row = [success_msg, status_code, requested_url, hostname, clientIP, serverIP, str(clientPort), str(serverPort), server_response_line]
        for i in range(len(csv_row)-1):
            csv_row[i] += ", "
        csv_row[-1] += "\n"
        log_file.writelines(csv_row)

def extract_status_line():
    server_response_line = http_header[:http_header.find("\n")].strip("\r")
    status_code = ((http_header[:http_header.find("\n")]).split(" "))[1]
    return [server_response_line, status_code]

def graceful_exit(exit_status):
    clientSocket.close()
    sys.exit(exit_status)

def terminal_success_message(success_msg, url, status_code):
    output_msg = success_msg
    if url != "N/A":
        output_msg += ": " + url
        if status_code != "N/A":
            output_msg += ", " + status_code
    print(output_msg)

'''
    Beginning of script (after function declarations)
'''

success_msg, status_code, requested_url, hostname, clientIP, clientPort, serverIP, serverPort, server_response_line = "Unsuccessful", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
url = "N/A"
if len(sys.argv) > 1:
    requested_url = sys.argv[1]
validate_arguments()

if sys.argv[1].find("http://") == 0:
    '''
        Remove http:// scheme from the url
        Extract port number from the given url
        Port, if it exists, will be a number between ":" and "/"
        Default port is 80
    '''
    url = (sys.argv[1])[7:]

    port_str, port = "", 80
    port_idx = (url.find(":") + 1) if url.find(":") > -1 else -1
    '''
        As given by the IBM Documentation, port number must be specified
        before the path, which is denoted by a "/"
    '''
    if url.find("/") > -1 and port_idx > url.find("/"):
        port_idx, end_url_idx = -1, -1
    else:
        end_url_idx = url.find(":")

    
    if port_idx > -1:
        while (port_idx < len(url)) and url[port_idx].isdigit:
            if(url[port_idx] == "/"):
                break
            port_str += url[port_idx]
            port_idx += 1
        port = int(port_str)

    url = url[:end_url_idx] + url[port_idx:]
    if len(sys.argv) == 3:
        hostname = sys.argv[2]
    else:
        hostname = url[:url.find("/")] if url.find("/") > -1 else url
else:
    server_response_line = "Requested URL does begin with http://"
    print(server_response_line)
    terminal_success_message(success_msg, url, status_code)
    sys.exit(1)

url_parts = url.split("/", 1)
url = url_parts[0]
request_query = url_parts[1] if len(url_parts) > 1 else ""
request_string = "GET /" + request_query + " HTTP/1.1\r\nHost:" + hostname + "\r\n\r\n"

clientSocket = socket(AF_INET, SOCK_STREAM)

'''
    Sets the timeout value for socket receive
'''
timeout_sec = 3
clientSocket.settimeout(timeout_sec)


'''
    May result in [errno 8] nodename nor servname provided, or not known
'''
try:
    '''
        Most web servers only listen on port 80 and port 443, so
        port numbers besides these will not establish a working connection.
    '''
    clientSocket.connect((url,port))
except Exception, e:
    '''
        An exception e is a tuple containing the exception number and message:
            Ex [Errno 8]: (8, 'nodename nor servname provided, or not known')
    '''
    if e.args[0] == "timed out":
        print("Connection timed out after " + str((timeout_sec*1000)+1) + " milliseconds")
        server_response_line = "Connection timed out"
    elif e.args[0] == 8 or e.args[0] == -2:
        print("Could not resolve host: " + hostname)
        server_response_line = "Could not resolve host"
    elif e.args[0] == 61 or e.args[0] == 111:
        print("Failed to connect to " + hostname + " port " + str(port) + ": Connection refused")
        server_response_line = "Connection refused"
    else:
        print e
    '''
        Must set the following values to N/A because we
        can only retrieve them with getsockname() and getpeername()
        if the socket object is connected successfully
    '''
    serverIP, serverPort = url if len(sys.argv) == 3 else "N/A", port
    csv_write(success_msg, status_code, requested_url, hostname, clientIP, serverIP, clientPort, serverPort, server_response_line)
    terminal_success_message(success_msg, url, status_code)
    graceful_exit(1)

'''
    Assign values for IPs and Ports from clientSocket functions
'''
clientIP, clientPort = clientSocket.getsockname()
serverIP, serverPort = clientSocket.getpeername()

'''
    May result in [errno 9] Bad file descriptor
    (has not happened in later development, thus not supported with log.csv entry)
'''
try:
    # .encode()/.decode() is not necessary for proper performance (omitted)
    clientSocket.send(request_string)
except Exception, e:
    print e
    graceful_exit(1)

http_response, http_header, html_content = "", "", ""

while True:
    try: 
        http_response += clientSocket.recv(2048)
        '''
            Search for the divide between the HTTP header and HTML content,
            and split along it into two variables: A complete HTTP header and
            possibly incomplete HTML content. 
        '''
        if len(http_response) == 0:
            server_response_line = "Empty reply from server"
            print(server_response_line)
            csv_write(success_msg, status_code, requested_url, hostname, clientIP, serverIP, clientPort, serverPort, server_response_line)
            terminal_success_message(success_msg, url, status_code)
            graceful_exit(1)

        if http_response.find("\r\n\r\n") > -1:
            http_header, html_content = http_response.split("\r\n\r\n", 1)

        '''
            Handling chunk encoded HTML pages as defined in the Project document
        '''
        if http_header.find("Transfer-Encoding: chunked") > -1:
            print("Chunk encoding is not supported")
            server_response_line, status_code = extract_status_line()
            csv_write(success_msg, status_code, requested_url, hostname, clientIP, serverIP, clientPort, serverPort, server_response_line)
            terminal_success_message(success_msg, url, status_code)
            sys.exit(1)

        if len(html_content):
            break
    except Exception, e:
        if e.args[0] == "timed out":
            print("Connection timed out after " + str((timeout_sec*1000)+1) + " milliseconds")
            server_response_line = "Connection timed out"
        elif e.args[0] == 54 or e.args[0] == 104:
            '''
                Catches connections with port 443
            '''
            server_response_line = "Recv failure: Connection reset by peer"
            print(server_response_line)
        else:
            print e

        csv_write(success_msg, status_code, requested_url, hostname, clientIP, serverIP, clientPort, serverPort, server_response_line)
        terminal_success_message(success_msg, url, status_code)
        graceful_exit(1)

'''
    Counteracting the split("\n\n") in case the Content-Length field is the last
    line of the HTTP header. We will need it to end with a newline character
    for a proceeding split("\n") command
'''
http_header += "\n"

'''
    These 3 lines find the value of the Content-Length field and convert it to int
'''
content_len_keyword = "Content-Length: "
if http_header.find(content_len_keyword) > -1:
    content_value_idx = http_header.find(content_len_keyword) + len(content_len_keyword)
else:
    # Try again with lowercase, as seen in neverssl on 03/01/22
    content_value_idx = http_header.find(content_len_keyword.lower()) + len(content_len_keyword)

try:
    content_length = int(http_header[content_value_idx:].split("\n")[0])
except Exception, e:
    server_response_line = "Content length is undefined"
    status_code = extract_status_line()[1]
    print(server_response_line)
    csv_write(success_msg, status_code, requested_url, hostname, clientIP, serverIP, clientPort, serverPort, server_response_line)
    terminal_success_message(success_msg, url, status_code)
    graceful_exit(1)

'''
    While the HTML content is not fully received, continue to prompt server for more data
    Once the length of the HTML content fulfills the expected content length, its done.
'''
while len(html_content) < content_length:
    try:
        html_content += clientSocket.recv(2048)
    except Exception, e:
        if e.args[0] == "timed out":
            print("Connection timed out after " + str((timeout_sec*1000)+1) + " milliseconds")
            server_response_line = "Connection timed out"
        else:
            print e
        csv_write(success_msg, status_code, requested_url, hostname, clientIP, serverIP, clientPort, serverPort, server_response_line)
        terminal_success_message(success_msg, url, status_code)
        graceful_exit(1)

'''
    Grab the first line of the HTTP header, pull out the status code
'''
server_response_line, status_code = extract_status_line()

if "200" in status_code:
    success_msg = "Success"

    html_file = open("HTTPoutput.html", "w")
    html_file.write(html_content)
    html_file.close()

terminal_success_message(success_msg, url, status_code)

csv_write(success_msg, status_code, requested_url, hostname, clientIP, serverIP, clientPort, serverPort, server_response_line)

graceful_exit(0)