package main

import (
    "fmt"
    "net"
    "os"
)

func main() {
    var (
        host = "127.0.0.1"
        port = "8080"
        remote = host + ":" + port
        data = make([]byte, 1024)
    )
    
    lis, err := net.Listen("tcp", remote)
    defer lis.Close()

    if err != nil {
        fmt.Println("Error listen", remote)
        os.Exit(-1)
    }

    for {
        conn, err := lis.Accept()
        if err != nil {
            continue
        }

        go func(con net.Conn) {
            fmt.Println("New connection: ", con.RemoteAddr())
            for {
                length, err := con.Read(data)
                if err != nil {
                    fmt.Printf("Client %v quit.\n", con.RemoteAddr())
                    con.Close()
                    return
                }
                con.Write(data[0:length])
            }
        }(conn)
    }
}

