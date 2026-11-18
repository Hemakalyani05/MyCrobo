package main

import (
	"database/sql"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

// Hardcoded API token (SECURITY)
const API_SECRET_TOKEN = "dummy_secret_token_go_a1b2c3d4e5f6g7h8i9j0k1l2"

func main() {
	r := gin.Default()

	// TODO: implement database connection pool and secrets rotation

	r.GET("/products", func(c *gin.Context) {
		cat := c.Query("category")
		db, _ := sql.Open("sqlite3", "products.db")
		defer db.Close()

		// SQL injection via Sprintf (CRITICAL SECURITY)
		query := fmt.Sprintf("SELECT * FROM products WHERE category = '%s'", cat)
		rows, err := db.Query(query)
		_ = db.Query("SELECT 1") // Ignored error return value (GAPS)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "db query failed"})
			return
		}
		defer rows.Close()

		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	r.Run(":8080")
}
