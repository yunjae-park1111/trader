# Changelog

All notable changes to this Nginx Ingress Controller project will be documented in this file.

## [v0.1.0] - 2025-08-30

### 🎉 Initial Release

### Added
- **Nginx Ingress Controller** with Cert-Manager integration
- **RouterProxy**: Dedicated SSL termination proxy service
- **External Service Integration**: Automatic Service/EndpointSlice creation for external IPs
- **Let's Encrypt SSL**: Automatic certificate issuance and renewal
- **Flexible Routing**: Path-based and port-based routing support

### Features

#### 🔐 SSL & Security
- SSL termination at RouterProxy level
- HTTP to HTTPS automatic redirect (port 80 → 443)
- Let's Encrypt integration with production/staging environments
- Support for IP-only access (no domain required)

#### 🌐 Routing & Proxy
- **targetPort**: Backend service actual port
- **proxyPort**: External access port (optional, defaults to targetPort)
- Path-based routing (`/`, `/app`, etc.)
- Backend redirect port rewriting (`proxy_redirect` rules)
- External IP integration (hardware routers, etc.)

#### ⚙️ Configuration
- Centralized configuration in `values.yaml`
- Global SSL settings (`global.ssl`)
- Optional domain configuration (`global.domain`)
- Multiple backend support
- Flexible resource allocation

#### 🏗️ Infrastructure
- K3s compatibility (ServiceLB support)
- LoadBalancer service type
- ClusterIP for ingress-nginx-controller
- EndpointSlice v1 compatibility (v1.33+)

### Architecture

```
Internet → RouterProxy (LoadBalancer)
    ├─ :80  → HTTP redirect to HTTPS
    ├─ :443 → HTTPS → HTTP proxy to ingress-nginx-controller
    └─ :10000 → HTTPS → HTTP proxy to external router (172.30.1.254:8899)
```

### Configuration Structure

```yaml
routerProxy:
  backends:
  - name: router
    serviceName: router-service
    external:
      ip: 172.30.1.254
      namespace: ingress-nginx
    routes:
    - path: /
      ports:
      - targetPort: 8899    # Backend port
        proxyPort: 10000    # External port (optional)
```

### Technical Improvements

#### Template Structure
- **router-proxy.yaml**: Dynamic nginx.conf generation with Helm templating
- **external-services.yaml**: Automatic Service/EndpointSlice creation
- **values.yaml**: Structured configuration with defaults and validation
- **basic-ingress.yaml**: Conditional host configuration

#### Helm Chart
- Umbrella chart with ingress-nginx and cert-manager dependencies
- CRD management separation
- Namespace-aware resource creation
- Resource limit configuration support

### Bug Fixes
- **Port collision**: Resolved K3s Traefik conflict
- **SSL compatibility**: Fixed TLS version and cipher configuration
- **Template validation**: Proper Helm template syntax and variable scoping
- **Service naming**: RFC 1123 compliant service port names
- **Endpoint deprecation**: Migrated from v1 Endpoints to v1 EndpointSlice
- **Type comparison**: Fixed Helm template integer/string comparison issues

### Breaking Changes
- Removed separate `externalForwarding` section (integrated into `routerProxy.backends`)
- Removed `ingress` backend from `routerProxy.backends` (path routing moved to RouterProxy)
- Changed `ingress-nginx-controller` service type from NodePort to ClusterIP

### Migration Notes
From initial TCP forwarding approach:
1. SSL termination moved from ingress-nginx to dedicated RouterProxy
2. External IP forwarding integrated into unified backend structure
3. Path-based routing consolidated under RouterProxy

### Known Issues
- SSL certificate issuance may take 5-10 minutes on first deployment
- Manual pod restart required after ConfigMap changes
- LoadBalancer external IP assignment depends on K3s ServiceLB

### Dependencies
- **Helm**: 3.x
- **Kubernetes**: 1.25+
- **ingress-nginx**: 4.8.3
- **cert-manager**: 1.13.2

### Tested Environments
- **K3s**: v1.33+
- **Platform**: Raspberry Pi cluster
- **Domain**: yjhome.kro.kr with Let's Encrypt
- **External Router**: 172.30.1.254:8899

---

## Development History

### Phase 1: Basic Setup
- Initial Helm chart creation with ingress-nginx dependency
- CRD conflict resolution (cert-manager.installCRDs: false)
- Basic Ingress resource creation

### Phase 2: SSL Integration  
- Cert-Manager integration with Let's Encrypt
- ClusterIssuer configuration (staging/production)
- SSL certificate automation

### Phase 3: TCP Forwarding
- Initial attempt with ingress-nginx TCP services
- LoadBalancer service configuration
- Port conflict resolution (Traefik removal)

### Phase 4: SSL Termination
- Recognition that Layer 4 TCP forwarding doesn't support SSL
- Development of dedicated RouterProxy for Layer 7 SSL termination
- Nginx configuration with SSL certificates

### Phase 5: Architecture Refinement
- Consolidation of all external traffic through RouterProxy
- ingress-nginx-controller moved to ClusterIP
- Integration of external IP forwarding

### Phase 6: Configuration Optimization
- values.yaml structure refinement
- Support for multiple backends and routes
- Flexible port mapping (targetPort/proxyPort)
- Optional SSL and domain configuration

### Phase 7: Template Unification
- Final structure: routes with top-level targetPort
- proxyPort as optional field with targetPort default
- Complete template consistency across all components

---

**🎯 Current Status**: Production Ready  
**📅 Last Updated**: August 30, 2025  
**🚀 Next Version**: TBD based on operational feedback
