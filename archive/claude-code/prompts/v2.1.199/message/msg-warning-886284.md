---
id: msg-warning-886284
name: Warning Message
category: message
subcategory: warning
source_line: 886284
---

),
          j("session.mint", { result: "fail", client_ip: R, err: ue }),
          await Ae({
            status: "denied",
            user_code: me.user_code,
            created_at: me.created_at,
          }),
          cZe("Sign-in could not be completed.")
        );
      }
    }
    if (U === "/oauth/token" && M.method === "POST") {
      let Z;
      try {
        Z = await M.formData();
      } catch {
        return Nae("invalid_request");
      }
      let re = Z.get("grant_type")?.toString();
      if (re === Bls) {
        let se = Z.get("device_code")?.toString();
        if (!se) return Nae("invalid_request");
        let ee = Gls(se),
          ne = await s.get(ee),
          oe = ne ? await jls(ne, l) : null;
        if (!oe) return Nae("expired_token");
        if (oe.status === "pending") {
          if ((await s.incr($Ar("poll", ee), Fls - 1)) > 1)
            return Nae("slow_down", 429);
          return Nae("authorization_pending");
        }
        if (oe.status === "denied")
          return (await s.del(ee), Nae("access_denied"));
        return (
          await s.del(ee),
          Response.json(
            {
              access_token: oe.access_token,
              refresh_token: oe.refresh_token,
              token_type: "Bearer",
              expires_in: oe.expires_in,
            },
            { headers: tln },
          )
        );
      }
      if (re === "refresh_token") {
        let se = Z.get("refresh_token")?.toString();
        if (!se) return Nae("invalid_request");
        try {
          let ee = await y.refresh(se),
            ne;
          try {
            ne = ee.claims();
          } catch {
            ne = void 0;
          }
          let oe, ie;
          if (ne === void 0) {
            if (!ee.access_token)
              throw Error(
                "IdP refresh response had neither id_token nor access_token",
              );
            oe = await y.userinfo(ee.access_token);
          } else ((oe = ne), (ie = await H(ne, ee.access_token)));
          let pe = await g(oe, "session.refresh", R, O, ie);
          return Response.json(
            {
              access_token: pe,
              refresh_token: ee.refresh_token ?? se,
              token_type: "Bearer",
              expires_in: t.session.ttl_hours * 3600,
            },
            { headers: tln },
          );
        } catch (ee) {
          let ne = ge(ee);
          (Tu("warn", 
