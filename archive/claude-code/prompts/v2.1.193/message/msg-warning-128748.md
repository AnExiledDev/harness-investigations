---
id: msg-warning-128748
name: Warning Message
category: message
subcategory: warning
source_line: 128748
---

 is deprecated. Please provide both keys, or provide neither and rely on the AWS credential provider chain.",
        );
      ((this.awsSecretKey = r),
        (this.awsAccessKey = o),
        (this.awsRegion = e),
        (this.awsSessionToken = s),
        (this.skipAuth = a.skipAuth ?? !1),
        (this.providerChainResolver = i));
    }
    validateHeaders() {}
    async prepareRequest(e, { url: t, options: n }) {
      if (this.skipAuth) {
        e.headers.delete("Authorization");
        return;
      }
      if (this.authToken) return;
      let r = this.awsRegion;
      if (!r)
        throw Error(
          "Expected 
