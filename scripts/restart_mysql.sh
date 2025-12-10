#!/bin/bash
# MySQL Restart Script for DBngin
# Run this when DBngin shows green but TablePlus can't connect

echo "🔍 Checking MySQL status on port 3307..."
echo ""

# Check if MySQL is actually running
if lsof -i :3307 > /dev/null 2>&1; then
    echo "✅ MySQL is already running on port 3307"
    ps aux | grep mysqld | grep -v grep
    exit 0
fi

echo "❌ MySQL is NOT running (even though DBngin might say it is)"
echo ""

# Try to stop any zombie processes
echo "🧹 Cleaning up any zombie processes..."
pkill -f "mysqld.*3307" 2>/dev/null
sleep 2

# Remove stale PID file
PID_FILE="/Users/melville/Library/Application Support/com.tinyapp.DBngin/Engines/mysql/AC590249-5B64-4206-AD9C-6A8BB8A855AC/mysql.pid"
if [ -f "$PID_FILE" ]; then
    echo "🗑️  Removing stale PID file..."
    rm "$PID_FILE"
fi

# Start MySQL
echo "🚀 Starting MySQL on port 3307..."
echo ""

/Users/Shared/DBngin/mysql/8.0.33/bin/mysqld \
    --datadir="/Users/melville/Library/Application Support/com.tinyapp.DBngin/Engines/mysql/AC590249-5B64-4206-AD9C-6A8BB8A855AC" \
    --port=3307 \
    --socket=/tmp/mysql_3307.sock \
    --pid-file="$PID_FILE" \
    --daemonize 2>&1

# Wait a moment for MySQL to start
sleep 2

# Check if it started successfully
if lsof -i :3307 > /dev/null 2>&1; then
    echo ""
    echo "✅ SUCCESS! MySQL is now running on port 3307"
    echo ""
    echo "📊 Connection details for TablePlus:"
    echo "   Host: 127.0.0.1"
    echo "   Port: 3307"
    echo "   User: root"
    echo "   Password: (empty or check DBngin)"
    echo ""
    echo "🎉 You can now connect with TablePlus!"
else
    echo ""
    echo "❌ Failed to start MySQL"
    echo ""
    echo "Check the error log:"
    echo "tail -50 '/Users/melville/Library/Application Support/com.tinyapp.DBngin/Engines/mysql/AC590249-5B64-4206-AD9C-6A8BB8A855AC/mysqld.local.err'"
fi
