export const PROVIDER_COLORS: Record<string, string> = {
  anthropic: '#D97757', // warm terracotta
  google:    '#4285F4', // Google Blue
  meta:      '#0668E1', // Meta blue (brightened for dark bg)
  mistral:   '#F59E0B', // warm amber
  openai:    '#10A37F', // OpenAI green-teal
  deepseek:  '#4F46E5', // indigo
  xai:       '#E5E7EB', // light gray
};

/** Derive a deterministic hue for a provider string (golden-angle spacing). */
export function providerHue(provider: string): number {
  let h = 0;
  for (let i = 0; i < provider.length; i++) {
    h = (h * 31 + provider.charCodeAt(i)) & 0xffffffff;
  }
  return (h >>> 0) % 360;
}

/** Get the provider-specific color, falling back to a deterministic HSL hue. */
export function getProviderColor(provider: string): string {
  return PROVIDER_COLORS[provider.toLowerCase()]
    ?? `hsl(${providerHue(provider)}, 55%, 48%)`;
}
