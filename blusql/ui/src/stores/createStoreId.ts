/*
 * Store Namespace Configuration
 * -----------------------------
 * This unique namespace ID ensures store identifiers remain distinct across
 * all applications and Assistant instances. It is automatically generated
 * during setup using a cryptographically secure random UUID.
 *
 * Important:
 * - Do not modify this value - changes could cause naming conflicts
 * - Always use the createStoreId function below when creating store IDs
 * - This system ensures safe coexistence of multiple app instances
 */
const APPLICATION_STORES_NAMESPACE: string = "e24c25dc-8dab-47a2-8f6b-678bc6ebb29f"

export const createStoreId = (
  storeName: string,
  namespace: string = APPLICATION_STORES_NAMESPACE,
): string => {
  return `${namespace}-${storeName}`
}
