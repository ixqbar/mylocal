package main

import (
    "fmt"
    "os"
    "encoding/json"
    "io/ioutil"
)

type jsonobject struct {
    Object ObjectType
}

type ObjectType struct {
    Buffer_size int
    Databases   []DatabasesType
}

type DatabasesType struct {
    Host   string
    User   string
    Pass   string
    Type   string
    Name   string
    Tables []TablesType
}

type TablesType struct {
    Name     string
    Statment string
    Regex    string
    Types    []TypesType
}

type TypesType struct {
    Id    string
    Value string
}

func main() {
    file, e := ioutil.ReadFile("./test.json")
    if e != nil {
        fmt.Printf("File error: %v\n", e)
        os.Exit(1)
    }
    fmt.Printf("%s\n", string(file))

    var jsontype jsonobject
    json.Unmarshal(file, &jsontype)
    fmt.Printf("buffer_size: %d\n", jsontype.Object.Buffer_size)
  	fmt.Printf("host:%s\n", jsontype.Object.Databases[0].Host) 
}
