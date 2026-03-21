import "@testing-library/jest-dom";
import { webcrypto } from "node:crypto";
import { TextDecoder, TextEncoder } from "node:util";

if (!globalThis.crypto) {
  globalThis.crypto = webcrypto as unknown as Crypto;
}

if (!(globalThis as any).TextEncoder) {
  (globalThis as any).TextEncoder = TextEncoder;
}

if (!(globalThis as any).TextDecoder) {
  (globalThis as any).TextDecoder = TextDecoder;
}
