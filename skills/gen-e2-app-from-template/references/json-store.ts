/**
 * JSON file repository — the ONLY module that touches the filesystem (ADR-003).
 *
 * Guarantees:
 *  - the file is loaded once and kept in memory
 *  - every mutation runs through a single promise queue (no interleaved writes)
 *  - writes are atomic: serialise to <file>.tmp, then rename over <file>
 */
import { promises as fs } from "node:fs";
import path from "node:path";
import type { Database } from "../domain/types.js";

const EMPTY_DATABASE: Database = { stalls: [], visits: [], spins: [] };

export interface JsonStoreOptions {
  /** Absolute path of the database file. */
  readonly filePath: string;
  /** Optional seed file used when `filePath` does not exist yet. */
  readonly seedPath?: string;
}

export class JsonStore {
  private data: Database = structuredClone(EMPTY_DATABASE);
  private writeQueue: Promise<void> = Promise.resolve();
  private loaded = false;

  constructor(private readonly options: JsonStoreOptions) {}

  /** Load the file (or the seed, or an empty database). Safe to call more than once. */
  async load(): Promise<void> {
    if (this.loaded) return;
    const existing = await readJsonIfExists(this.options.filePath);
    if (existing) {
      this.data = normalise(existing);
    } else {
      const seed = this.options.seedPath ? await readJsonIfExists(this.options.seedPath) : null;
      this.data = seed ? normalise(seed) : structuredClone(EMPTY_DATABASE);
      await this.persist();
    }
    this.loaded = true;
  }

  /** Read-only snapshot. Callers must not mutate the returned arrays. */
  snapshot(): Readonly<Database> {
    this.assertLoaded();
    return this.data;
  }

  /**
   * Apply a mutation and persist it. Mutations are serialised, so `mutate`
   * callbacks always see the latest state and never race each other.
   */
  mutate<T>(fn: (db: Database) => T): Promise<T> {
    this.assertLoaded();
    let result!: T;
    const run = this.writeQueue.then(async () => {
      const draft = structuredClone(this.data);
      result = fn(draft);
      this.data = draft;
      await this.persist();
    });
    // Keep the queue alive even if this write fails.
    this.writeQueue = run.catch(() => undefined);
    return run.then(() => result);
  }

  private async persist(): Promise<void> {
    const { filePath } = this.options;
    await fs.mkdir(path.dirname(filePath), { recursive: true });
    const tmpPath = `${filePath}.tmp`;
    await fs.writeFile(tmpPath, JSON.stringify(this.data, null, 2), "utf8");
    await fs.rename(tmpPath, filePath);
  }

  private assertLoaded(): void {
    if (!this.loaded) throw new Error("JsonStore used before load()");
  }
}

async function readJsonIfExists(filePath: string): Promise<unknown | null> {
  try {
    const raw = await fs.readFile(filePath, "utf8");
    return JSON.parse(raw) as unknown;
  } catch (error) {
    if (isMissingFile(error)) return null;
    throw new Error(`Could not read database file ${filePath}: ${(error as Error).message}`);
  }
}

function isMissingFile(error: unknown): boolean {
  return typeof error === "object" && error !== null && (error as NodeJS.ErrnoException).code === "ENOENT";
}

function normalise(raw: unknown): Database {
  const candidate = (typeof raw === "object" && raw !== null ? raw : {}) as Partial<Database>;
  return {
    stalls: Array.isArray(candidate.stalls) ? candidate.stalls : [],
    visits: Array.isArray(candidate.visits) ? candidate.visits : [],
    spins: Array.isArray(candidate.spins) ? candidate.spins : [],
  };
}
