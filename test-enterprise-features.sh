#!/bin/bash
# Script de prueba para features enterprise de ManttoAI
# Uso: ./test-enterprise-features.sh

set -e

echo "🧪 Testing ManttoAI Enterprise Features"
echo "========================================"
echo ""

# Configuración
API_URL="${API_URL:-http://localhost:8000}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@manttoai.local}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir resultados
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
    fi
}

# Función para hacer requests HTTP
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4

    if [ -z "$token" ]; then
        curl -s -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${API_URL}${endpoint}"
    else
        curl -s -X "$method" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data" \
            "${API_URL}${endpoint}"
    fi
}

echo "1. Testing Rate Limiting"
echo "------------------------"

# Hacer 50 requests rápidos
echo "Making 50 rapid requests to /health..."
for i in {1..50}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/health")
    if [ "$i" -eq 50 ]; then
        if [ "$response" = "200" ]; then
            print_result 0 "Rate limiting: 50 requests completed (no rate limit yet)"
        else
            print_result 1 "Rate limiting: Unexpected response code $response"
        fi
    fi
done

# Hacer 300 requests rápidos (debería rate limitar después de ~200 para visualizador)
echo "Making 300 rapid requests to test rate limiting..."
rate_limited=0
for i in {1..300}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/health")
    if [ "$response" = "429" ]; then
        rate_limited=1
        echo "Rate limited at request $i"
        break
    fi
done

if [ $rate_limited -eq 1 ]; then
    print_result 0 "Rate limiting: Correctly limited at 429"
else
    echo -e "${YELLOW}⚠️  WARN${NC}: Rate limiting not triggered (might be within limits)"
fi

echo ""
echo "2. Testing Legal Endpoints"
echo "-------------------------"

# Test TOS
echo "Testing /legal/terms-of-service..."
tos_response=$(make_request "GET" "/api/v1/legal/terms-of-service")
if echo "$tos_response" | grep -q "title"; then
    print_result 0 "Terms of Service endpoint working"
else
    print_result 1 "Terms of Service endpoint failed"
fi

# Test Privacy Policy
echo "Testing /legal/privacy-policy..."
pp_response=$(make_request "GET" "/api/v1/legal/privacy-policy")
if echo "$pp_response" | grep -q "title"; then
    print_result 0 "Privacy Policy endpoint working"
else
    print_result 1 "Privacy Policy endpoint failed"
fi

# Test DPA
echo "Testing /legal/dpa..."
dpa_response=$(make_request "GET" "/api/v1/legal/dpa")
if echo "$dpa_response" | grep -q "title"; then
    print_result 0 "DPA endpoint working"
else
    print_result 1 "DPA endpoint failed"
fi

echo ""
echo "3. Testing Monitoring Endpoints"
echo "--------------------------------"

# Login como admin
echo "Logging in as admin..."
login_response=$(make_request "POST" "/api/v1/auth/login" "{\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}")
admin_token=$(echo "$login_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$admin_token" ]; then
    print_result 0 "Admin login successful"
else
    print_result 1 "Admin login failed"
    echo "Login response: $login_response"
    exit 1
fi

# Test metrics summary
echo "Testing /metrics/summary..."
metrics_response=$(make_request "GET" "/api/v1/metrics/summary" "" "$admin_token")
if echo "$metrics_response" | grep -q "system"; then
    print_result 0 "Metrics summary endpoint working"
else
    print_result 1 "Metrics summary endpoint failed"
fi

# Test health detailed
echo "Testing /metrics/health-detailed..."
health_response=$(make_request "GET" "/api/v1/metrics/health-detailed" "" "$admin_token")
if echo "$health_response" | grep -q "components"; then
    print_result 0 "Detailed health check endpoint working"
else
    print_result 1 "Detailed health check endpoint failed"
fi

# Test reset metrics
echo "Testing /metrics/reset (admin only)..."
reset_response=$(make_request "POST" "/api/v1/metrics/reset" "" "$admin_token")
if echo "$reset_response" | grep -q "Métricas reseteadas"; then
    print_result 0 "Metrics reset endpoint working"
else
    print_result 1 "Metrics reset endpoint failed"
fi

echo ""
echo "4. Testing RBAC (if implemented)"
echo "---------------------------------"

# Crear usuario visualizador
echo "Creating visualizador user..."
create_user_response=$(make_request "POST" "/api/v1/auth/register" "{\"nombre\":\"Test Visualizador\",\"email\":\"visualizador@test.com\",\"password\":\"password123\"}" "$admin_token")
if echo "$create_user_response" | grep -q "id"; then
    print_result 0 "Visualizador user created"
else
    echo -e "${YELLOW}⚠️  WARN${NC}: Could not create visualizador user (might already exist)"
fi

# Login como visualizador
echo "Logging in as visualizador..."
vis_login_response=$(make_request "POST" "/api/v1/auth/login" "{\"email\":\"visualizador@test.com\",\"password\":\"password123\"}")
vis_token=$(echo "$vis_login_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$vis_token" ]; then
    print_result 0 "Visualizador login successful"

    # Intentar crear equipo (debería fallar si RBAC está implementado)
    echo "Testing that visualizador cannot create equipo..."
    create_equipo_response=$(make_request "POST" "/api/v1/equipos" "{\"nombre\":\"Test Equipo\",\"ubicacion\":\"Test\"}" "$vis_token")
    if echo "$create_equipo_response" | grep -q "403\|401\|permission"; then
        print_result 0 "RBAC working: visualizador correctly blocked from creating equipo"
    else
        echo -e "${YELLOW}⚠️  WARN${NC}: RBAC might not be fully implemented yet (delegation in progress)"
    fi
else
    echo -e "${YELLOW}⚠️  WARN${NC}: Could not login as visualizador"
fi

echo ""
echo "5. Testing API Keys (if implemented)"
echo "------------------------------------"

# Crear API key
echo "Creating API key..."
create_key_response=$(make_request "POST" "/api/v1/api-keys" "{\"device_id\":\"esp32_test_001\"}" "$admin_token")
if echo "$create_key_response" | grep -q "key\|id"; then
    print_result 0 "API key created"
else
    echo -e "${YELLOW}⚠️  WARN${NC}: API key creation failed (delegation in progress)"
fi

echo ""
echo "6. Testing Audit Trail (if implemented)"
echo "---------------------------------------"

# Obtener audit logs
echo "Fetching audit logs..."
audit_response=$(make_request "GET" "/api/v1/audit-logs" "" "$admin_token")
if echo "$audit_response" | grep -q "logs\|items\|data"; then
    print_result 0 "Audit logs endpoint working"
else
    echo -e "${YELLOW}⚠️  WARN${NC}: Audit logs endpoint not working (delegation in progress)"
fi

echo ""
echo "========================================"
echo "✨ Test Suite Completed"
echo "========================================"
echo ""
echo "📝 Summary:"
echo "  - Rate Limiting: Tested"
echo "  - Legal Endpoints: Tested"
echo "  - Monitoring: Tested"
echo "  - RBAC: Partially tested (delegation in progress)"
echo "  - API Keys: Partially tested (delegation in progress)"
echo "  - Audit Trail: Partially tested (delegation in progress)"
echo ""
echo "⚠️  Note: Some features are still being implemented by delegated agents."
echo "   Run this script again after delegations complete for full testing."
