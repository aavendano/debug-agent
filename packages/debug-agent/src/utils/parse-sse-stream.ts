import { createParser, type EventSourceMessage } from "eventsource-parser";

export interface ParsedSseEvent {
  event: string;
  data: string;
}

export const parseSseStream = async function* (
  stream: ReadableStream<Uint8Array>,
): AsyncGenerator<ParsedSseEvent, void, void> {
  const pendingEvents: ParsedSseEvent[] = [];
  const parser = createParser({
    onEvent: (message: EventSourceMessage) => {
      pendingEvents.push({ event: message.event || "message", data: message.data });
    },
  });

  const textDecoder = new TextDecoder();
  const reader = stream.getReader();
  try {
    while (true) {
      const { value: chunk, done } = await reader.read();
      if (done) break;
      parser.feed(textDecoder.decode(chunk, { stream: true }));
      while (pendingEvents.length > 0) {
        const next = pendingEvents.shift();
        if (next) yield next;
      }
    }
  } finally {
    reader.releaseLock();
  }
};
