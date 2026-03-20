#!/bin/bash

echo "=== Staff Portal API Test Script ==="
echo ""

API_BASE="http://localhost:8000"

echo "1. Test: Boss checking revenue (GET /analytics/revenue)"
echo "-------------------------------------------"
RESPONSE=$(curl -s "$API_BASE/analytics/revenue")
echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
echo ""

echo "2. Test: Create an order for testing"
echo "-------------------------------------------"
ORDER_RESPONSE=$(curl -s -X POST "$API_BASE/order" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"id": 1, "quantity": 2}]}')
echo "$ORDER_RESPONSE" | jq . 2>/dev/null || echo "$ORDER_response"
ORDER_ID=$(echo "$ORDER_RESPONSE" | jq -r '.orderId' 2>/dev/null)
echo "Created Order ID: $ORDER_ID"
echo ""

echo "3. Test: Chef starts cooking (PATCH /order/{id}/status)"
echo "-------------------------------------------"
curl -s -X PATCH "$API_BASE/order/$ORDER_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "COOKING"}' | jq . 2>/dev/null || echo "Updated to COOKING"
echo ""

echo "4. Test: Chef marks as ready (PATCH /order/{id}/status)"
echo "-------------------------------------------"
curl -s -X PATCH "$API_BASE/order/$ORDER_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "READY"}' | jq . 2>/dev/null || echo "Updated to READY"
echo ""

echo "5. Test: Waiter marks as served (PATCH /order/{id}/status)"
echo "-------------------------------------------"
curl -s -X PATCH "$API_BASE/order/$ORDER_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "SERVED"}' | jq . 2>/dev/null || echo "Updated to SERVED"
echo ""

echo "6. Test: Cashier completes payment (PATCH /order/{id}/status)"
echo "-------------------------------------------"
curl -s -X PATCH "$API_BASE/order/$ORDER_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "PAID"}' | jq . 2>/dev/null || echo "Updated to PAID"
echo ""

echo "7. Test: Boss checks revenue after payment (GET /analytics/revenue)"
echo "-------------------------------------------"
curl -s "$API_BASE/analytics/revenue" | jq . 2>/dev/null || echo "$RESPONSE"
echo ""

echo "=== All tests completed ==="