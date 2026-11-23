# TLS, load balancing and proxy choices

Short decisions, with what each one costs.

**TLS ends at the load balancer.** Certificates live in ACM and renew themselves. Tasks speak plain HTTP on a private subnet. The cost is that traffic between the load balancer and a task is not encrypted. If a control requires encryption inside the VPC, run HTTPS to the task and set the target group protocol to HTTPS, at the price of certificate handling in every service. Flip to it when a requirement says so, not before.

**Policy `ELBSecurityPolicy-TLS13-1-2-2021-06`.** TLS 1.3 and 1.2 only. Old clients on TLS 1.0 or 1.1 cannot connect. Check client logs before tightening further.

**HTTP redirects with a 301, it does not serve.** Port 80 stays open only to redirect. A client that ignores the redirect never reaches the app.

**Health check on `/healthz`, 200 to 399.** Two good checks to join, three bad to leave. Keep the check cheap and local: if it calls the database, a database blip pulls every task out at once.

**`drop_invalid_header_fields` on.** The load balancer drops malformed headers instead of passing them to the app. This blocks a class of request smuggling at the edge.

**Idle timeout 60 seconds.** If the app holds connections longer, set the app's keep-alive above the load balancer's, or you get sporadic 502s when the app closes first.

**If you run your own proxy (nginx, Envoy) in front of the app.** Set `X-Forwarded-For` and `X-Forwarded-Proto` from the load balancer and trust them only from the load balancer's security group. Match timeouts to the load balancer. Run a config test in CI (`nginx -t`) so a bad config never ships.
