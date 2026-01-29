package main

import (
	"os"

	"github.com/johnamadeo/server"
)

// DuplicateKeyErr : Error message when user tries to insert row with duplicate key
const DuplicateKeyErr = "duplicate key value violates unique constraint"

// getEnv : Get environment variable with fallback default
func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

// LocalDBConnection :
var LocalDBConnection = server.LocalDBConnection{
	User:   getEnv("DB_USER", "postgres"),
	DBName: getEnv("DB_NAME", "mealbot"),
}
