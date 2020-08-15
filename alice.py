from GNet.connection import GNetConnection

with GNetConnection("Alice", "Bob") as conn:
    print("Starting connection with Bob. You can end the connection by sending an empty message.")
    send = True
    while True:
        message = input("Message to Bob: ") if send else conn.receiveEncripted()
        
        if send:
            conn.sendEncripted(message)
            if message == "":
                break
        else:
            print("Received from Bob: ", message)
            if message is None:
                break
        
        send = not send

