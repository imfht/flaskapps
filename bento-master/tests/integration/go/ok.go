package main

import (
  "fmt"
  "os"
)

func main() {
	username := os.Getenv("USERNAME")
	password := os.Getenv("PASSWORD")
	fmt.Println("Doing something with: ", username, password)
}
