from GNet.connection import GNetConnection

with GNetConnection("Bob", "Alice") as conn:
    print("Starting connection with Alice. You can end the connection by sending an empty message.")
    send = False
    while True:
        message = input("Message to Alice: ") if send else conn.receiveEncripted()
        
        if send:
            conn.sendEncripted(message)
            if message == "":
                break
        else:
            print("Recieved from Alice: ", message)
            if message is None:
                break
        
        send = not send

