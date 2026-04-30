import socket
import sys
import os

from torch.fx.passes.graph_manipulation import size_bytes
from torch.onnx.symbolic_opset11 import chunk
from torch.utils.hipify.hipify_python import value
from torchvision import message


def main():
    if len(sys.argv) != 4:
        print("Usage: python tuple_space_client.py <server-hostname> <server-port> <input-file>")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    input_file_path = sys.argv[3]

    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' does not exist.")
        sys.exit(1)

    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # TASK 1: Create a TCP/IP socket and connect it to the server.
    # Hint: socket.socket(socket.AF_INET, socket.SOCK_STREAM) creates the socket.
    # Then call sock.connect((hostname, port)) to connect.
    #AF_INET  means IPv4 address
    #SOCK_STREAM means TCP protocol
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #connect to the server
    sock.connect((hostname,port))

    try:
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(" ", 2)
            cmd = parts[0]
            message = ""

            # TASK 2: Build the protocol message string to send to the server.
            # Format:  "NNN X key"        for READ / GET
            #          "NNN P key value"   for PUT
            # where NNN is the total message length as a zero-padded 3-digit number,
            # X is "R" for READ and "G" for GET.
            # Hint: for READ/GET, size = 6 + len(key). For PUT, size = 7 + len(key) + len(value).
            # Reject lines with invalid format or key+" "+value > 970 chars.
            if cmd == "READ" or cmd =="GET":# check is key is provided
                if len(parts)<2:
                    print("miss key")
                    continue


                key = parts[1]

                       #ensure read or get
                op=""
                if cmd =="READ":
                    op ="R"
                if cmd =="GET":
                    op ="G"
                    #6=3number +space+ letter+space+lenn(ket)
                total_length= 6+len(key)
                len_str=str(total_length)
                while len(len_str)<3:
                    len_str="0"+len_str
                message =len_str +""+op+""+key



                    #PUT command
                if cmd =="PUT":
                    if len(parts)<3:
                        print("miss key")
                        continue

                    key=parts[1]
                    value=parts[2]

                    #value and key cannot beyond 999chars
                    if len(key)>999:
                        print("key too long")
                        continue

                    if len(value)>999:
                        print("value too long")
                        continue

                        #key+space+calue <= 970chars
                    if len(key+""+value)>970:
                        print("key+value beyond 970chars")
                        continue

                        #calculate the total size
                    total_length=7+len(key)+len(value)
                    len_str = str(total_length)
                    while len(len_str) < 3:
                        len_str = "0" + len_str
                    message = len_str + "P" + op + "" + key


                    #unknown command
                    if cmd !="READ" and cmd != "GET" and cmd!="PUT":
                        print("unknown command")
                        continue






            # TASK 3: Send the message to the server, then receive the response.
            # - Send:    sock.sendall(message.encode())
            # - Receive: first read 3 bytes to get the response size (like the server does).
            #            Then read the remaining (size - 3) bytes to get the response body.

            #send message
            sock.sendall(message.encode())
            #read first 3bytes it is response size
            size_bytes=b""
            while len(size_bytes)<3:
                a =sock.recv(3-len(size_bytes))
                if not a:
                    print("connection closed")
                    break
                size_bytes+=a
            # Convert received byte data to string, then convert to integer length
            size_str=size_bytes.decode()
            response_size= int(size_str)

            #read the rest of the responce body
            size_bytes=b""
            remaining=response_size-3
            while len(size_bytes)<remaining:
                a=sock.recv(remaining-len(size_bytes))
                if not a :
                    print("connection closed")
                    return
                size_bytes += a





            response = response_buffer.decode().strip()
            print(f"{line}: {response}")

    except (socket.error, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        # TASK 4: Close the socket when done (already called for you — explain why
        # finally: is the right place to do this even if an error occurs above).

        #finally always rusn, even if try has an error
        #socket gets closed properly so donot waste system resource
        if sock is not  None:
           sock.close()

if __name__ == "__main__":
    main()