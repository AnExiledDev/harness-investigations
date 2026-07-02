---
id: msg-warning-162429
name: Warning Message
category: message
subcategory: warning
source_line: 162429
---

,
    );
}
var MXr,
  vMi,
  CRn,
  eSe,
  IRn,
  BGd,
  kRn = "gateway TLS certificate does not match the pinned fingerprint";
var RRn = E(() => {
  C4e();
  ut();
  xW();
  Wg();
  KW();
  ((MXr = require("dns/promises")),
    (vMi = require("http")),
    (CRn = require("https")),
    (eSe = require("net")),
    (IRn = require("tls")),
    (BGd = new Set(["localhost", "127.0.0.1", "[::1]"])));
});
function kMi() {
  return xMi;
}
function hre() {
  xMi.clear();
}
var xMi;
var nlt = E(() => {
  xMi = new Map();
});
var qF = {};
lt(qF, {
  withOAuthRefreshLock: () => sJr,
  waitForRotatedEnvToken: () => GMi,
  validateForceLoginOrg: () => fue,
  toAccountInfo: () => _Ut,
  shouldUseWIFAuth: () => AH,
  saveOAuthTokensIfNeeded: () => iRe,
  saveApiKey: () => dWr,
  restoreGatewayAuth: () => qXr,
  resetEnvDerivedAuthCaches: () => tJr,
  resetAwsAuthRefreshCooldown: () => llt,
  resetAuthFailureTracking: () => nJr,
  removeApiKey: () => eJr,
  refreshGcpCredentialsIfNeeded: () => sWe,
  refreshGcpAuth: () => UMi,
  refreshAwsAuth: () => MRn,
  refreshAndGetAwsCredentials: () => MW,
  readFreshOAuthAccessToken: () => rJr,
  prefetchGcpCredentialsIfSafe: () => ZXr,
  prefetchAwsCredentialsAndBedRockInfoIfSafe: () => hUt,
  prefetchApiKeyFromApiKeyHelperIfSafe: () => XXr,
  oauthRefreshLockOptions: () => NXr,
  noteAuthRecoveryOutcome: () => rlt,
  isWIFDispatchAuth: () => GXr,
  isUsing3PServices: () => qX,
  isTeamSubscriberAsync: () => S3d,
  isTeamSubscriber: () => u3d,
  isTeamPremiumSubscriberAsync: () => E3d,
  isTeamPremiumSubscriber: () => s0e,
  isProSubscriberAsync: () => T3d,
  isProSubscriber: () => dbe,
  isOverageProvisioningAllowedAsync: () => y3d,
  isOverageProvisioningAllowed: () => aRe,
  isOtelHeadersHelperFromProjectOrLocalSettings: () => VMi,
  isOAuthRefreshKnownDead: () => $Rn,
  isMaxSubscriberAsync: () => b3d,
  isMaxSubscriber: () => Oce,
  isHostManagedProviderAuth: () => GF,
  isGcpAuthRefreshFromProjectSettings: () => QXr,
  isFirstPartyManagedOAuthContext: () => gUt,
  isExpectedOAuthRefreshError: () => WMi,
  isEnterpriseSubscriberAsync: () => A3d,
  isEnterpriseSubscriber: () => clt,
  isEnterprisePAYGSubscriberAsync: () => H3d,
  isEnterprisePAYGSubscriber: () => ube,
  isCustomApiKeyApproved: () => n3d,
  isConsumerSubscriberAsync: () => v3d,
  isConsumerSubscriber: () => rSe,
  isClaudeAISubscriberAsync: () => AUt,
  isClaudeAISubscriber: () => Eo,
  isAwsCredentialExportFromProjectSettings: () => KXr,
  isAwsAuthRefreshFromProjectSettings: () => pWe,
  isAnthropicAuthEnabledAsync: () => EUt,
  isAnthropicAuthEnabled: () => SS,
  is1PApiCustomerAsync: () => h3d,
  is1PApiCustomer: () => gWe,
  hasStoredOAuthToken: () => lA,
  hasStoredOAuthRefreshToken: () => l3d,
  hasProfileScopeAsync: () => g3d,
  hasProfileScope: () => FI,
  hasOpusAccessAsync: () => _3d,
  hasOpusAccess: () => c3d,
  hasOAuthScope: () => mWe,
  hasAnthropicDirectApiKey: () => Pqr,
  hasAnthropicApiKeyAuthAsync: () => m3d,
  hasAnthropicApiKeyAuth: () => PRn,
  hasAnthropicApiKey: () => n1t,
  handleOAuth401Error: () => LF,
  getSubscriptionTypeAsync: () => pue,
  getSubscriptionType: () => $i,
  getSubscriptionNameAsync: () => QMi,
  getSubscriptionName: () => BRn,
  getStoredOAuthTokenExpiresAt: () => NRn,
  getStoredOAuthSubscriptionType: () => yUt,
  getSeatTierAsync: () => JMi,
  getSeatTier: () => qMi,
  getRateLimitTierAsync: () => XMi,
  getRateLimitTier: () => s5,
  getOtelHeadersHelperLastFailure: () => aJr,
  getOtelHeadersFromHelper: () => lJr,
  getOrgModelDefaultCache: () => wqr,
  getOauthAccountInfoAsync: () => fUt,
  getOauthAccountInfo: () => Bc,
  getModelAccessCache: () => N1t,
  getConfiguredAwsAuthRefresh: () => nSe,
  getConfiguredApiKeyHelper: () => bL,
  getClaudeAIOAuthTokensAsync: () => _L,
  getClaudeAIOAuthTokens: () => Js,
  getAuthTokenSourceAsync: () => YMi,
  getAuthTokenSource: () => BI,
  getApiKeySourceSafe: () => VXr,
  getApiKeyHelperElapsedMs: () => YXr,
  getApiKeyFromConfigOrMacOSKeychainAsync: () => bUt,
  getApiKeyFromConfigOrMacOSKeychain: () => fWe,
  getApiKeyFromApiKeyHelperCached: () => pUt,
  getApiKeyFromApiKeyHelper: () => Yat,
  getAnthropicApiKeyWithSourceSafe: () => WX,
  getAnthropicApiKeyWithSourceAsyncSafe: () => KMi,
  getAnthropicApiKeyWithSourceAsync: () => SUt,
  getAnthropicApiKeyWithSource: () => YI,
  getAnthropicApiKeySafe: () => Fne,
  getAnthropicApiKeyAsync: () => f3d,
  getAnthropicApiKey: () => $W,
  getAdditionalModelOptionsCache: () => ibe,
  getAccountInformationAsync: () => w3d,
  getAccountInformation: () => hWe,
  describeHowToDisableAuthTokenSource: () => dWe,
  clearWIFAuthDebugOnceCacheForTesting: () => GGd,
  clearOtelHeadersCache: () => p3d,
  clearOAuthTokenCache: () => WF,
  clearGcpCredentialsCache: () => sRe,
  clearAwsCredentialsCache: () => due,
  clearApiKeyHelperCache: () => alt,
  checkGcpCredentialsValid: () => FMi,
  checkAndRefreshOAuthTokenIfNeededWithOutcome: () => ORn,
  checkAndRefreshOAuthTokenIfNeeded: () => Vg,
  calculateApiKeyHelperTTL: () => BMi,
  acquireOAuthRefreshLock: () => oJr,
  __resetKnownDeadRefreshTokensForTest: () => r3d,
  SDK_OAUTH_REFRESH_ENTRYPOINTS: () => WXr,
});
function ilt() {
  return at(process.env.CLAUDE_CODE_REMOTE) || d8();
}
function GF() {
  return De.CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST;
}
function gUt() {
  return (
    ilt() &&
    !process.env.CLAUDE_CODE_HOST_AUTH_ENV_VAR &&
    process.env.CLAUDE_CODE_ENTRYPOINT !== "claude-desktop-3p"
  );
}
function GGd() {
  ($Mi.cache.clear?.(), OMi.cache.clear?.());
}
function AH() {
  if (!Ovn()) return !1;
  if (
    Dd() ||
    process.env.ANTHROPIC_UNIX_SOCKET ||
    ilt() ||
    GF() ||
    process.env.ANTHROPIC_AUTH_TOKEN ||
    process.env.CLAUDE_CODE_OAUTH_TOKEN ||
    P8() ||
    bL() ||
    at(process.env.CLAUDE_CODE_USE_BEDROCK) ||
    at(process.env.CLAUDE_CODE_USE_VERTEX) ||
    at(process.env.CLAUDE_CODE_USE_FOUNDRY) ||
    at(process.env.CLAUDE_CODE_USE_ANTHROPIC_AWS) ||
    at(process.env.CLAUDE_CODE_USE_MANTLE)
  )
    return !1;
  if (D8() === "profile-implicit") {
    let e = Js();
    if (i4(e?.scopes) && e?.accessToken && fGe() === "user_oauth")
      return ($Mi(), !1);
  }
  return (OMi(), !0);
}
function GXr() {
  return $W() === null && AH();
}
async function qXr() {
  if (at(process.env.CLAUDE_CODE_USE_GATEWAY)) {
    let e = process.env.ANTHROPIC_BASE_URL,
      t = process.env.ANTHROPIC_AUTH_TOKEN;
    if (e && t) {
      let n;
      try {
        n = xRn(e);
      } catch (o) {
        throw Error(
          
