#!/bin/bash
# Check MySQL status

echo "🔍 Checking MySQL processes..."
ps aux | grep -i mysql | grep -v grep

echo ""
echo "🔍 Checking ports 3306 and 3307..."
lsof -i :3306 -i :3307

echo ""
echo "🔍 Checking if we can connect..."
mysql -h 127.0.0.1 -P 3307 -u root -e "SELECT 'MySQL is working!' as status;" 2>&1 || echo "❌ Cannot connect to MySQL"
