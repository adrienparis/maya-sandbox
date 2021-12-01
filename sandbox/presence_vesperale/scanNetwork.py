# # from socket import *
# import socket
# import time
# startTime = time.time()


# a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# location = ("192.168.1.19", 15555)

# result_of_check = a_socket.connect_ex(location)


# if result_of_check == 0:

#    print("Port is open")

# else:

#    print("Port is not open")

# # if __name__ == '__main__':
# #    target = input('Enter the host to be scanned: ')
# #    t_IP = gethostbyname(target)
# #    print ('Starting scan on host: ', t_IP)
   
# #    for i in range(50, 500):
# #       s = socket(AF_INET, SOCK_STREAM)
      
# #       conn = s.connect_ex((t_IP, i))
# #       if(conn == 0) :
# #          print ('Port %d: OPEN' % (i,))
# #       s.close()
# # print('Time taken:', time.time() - startTime)


    # except KeyboardInterrupt:
    #     print('\nExiting program.')
    #     sys.exit()
    # except socket.gaierror:
    #     print('Hostname could not be resolved.')
    #     sys.exit()
    # except socket.timeout:
    #     print('Connection timed out.')
    #     sys.exit()
    # except socket.error:
    #     print("Couldn't connect to server.")
    #     sys.exit()


import socket, sys


def IsPortOpenned(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    result = s.connect_ex((ip, port))
    s.close()
    return result == 0

if __name__ == "__main__":
    for i in range(1,255):
        for j in range(0,255):
            adress = "192.168.{}.{}".format(i, j)
            if IsPortOpenned(adress, 15555):
                print(socket.gethostbyaddr(adress))
            
            sys.stdout.write('\r')
            # the exact output you're looking for:
            iper, jper = int(i*100/255), int(j*100/255)
            sys.stdout.write("[%-20s] %d%%\t[%-20s] %d%%" % ('='*int(iper*20/100), i, '='*int(jper*20/100), jper))
            sys.stdout.flush()
    