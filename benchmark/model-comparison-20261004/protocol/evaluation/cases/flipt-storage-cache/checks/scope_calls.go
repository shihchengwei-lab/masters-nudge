package main

import (
    "encoding/json"
    "go/ast"
    "go/parser"
    "go/token"
    "os"
    "strconv"
)

type document struct {
    Path string `json:"path"`
    Before string `json:"before"`
    After string `json:"after"`
    Names []string `json:"names"`
}

func calls(source string, names []string) []string {
    file, err := parser.ParseFile(token.NewFileSet(), "caller.go", source, 0)
    if err != nil { return nil }
    selected := make(map[string]bool)
    for _, name := range names { selected[name] = true }
    var result []string
    ast.Inspect(file, func(node ast.Node) bool {
        call, ok := node.(*ast.CallExpr)
        if !ok { return true }
        name := ""
        switch fun := call.Fun.(type) {
        case *ast.Ident: name = fun.Name
        case *ast.SelectorExpr: name = fun.Sel.Name
        }
        if selected[name] { result = append(result, name+"/"+strconv.Itoa(len(call.Args))) }
        return true
    })
    return result
}

func main() {
    var documents []document
    if err := json.NewDecoder(os.Stdin).Decode(&documents); err != nil { panic(err) }
    type comparison struct {
        Path string `json:"path"`
        Before []string `json:"before"`
        After []string `json:"after"`
    }
    result := []comparison{}
    for _, doc := range documents {
        result = append(result, comparison{doc.Path, calls(doc.Before, doc.Names), calls(doc.After, doc.Names)})
    }
    if err := json.NewEncoder(os.Stdout).Encode(result); err != nil { panic(err) }
}
