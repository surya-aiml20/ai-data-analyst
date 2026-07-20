import { Send, Sparkles } from "lucide-react";
import { FormEvent, useState } from "react";
import type { QueryResponse } from "../types/api";
import { Button } from "./Button";
import { ChartRenderer } from "./ChartRenderer";

type Message = {
  role: "user" | "assistant";
  content: string;
  response?: QueryResponse;
};

type Props = {
  disabled: boolean;
  onAsk: (question: string) => Promise<QueryResponse>;
};

const suggestions = [
  "Which region generated the highest revenue?",
  "Show monthly sales trends.",
  "Which products are underperforming?",
  "Generate SQL for this analysis.",
  "Detect anomalies in the dataset."
  ,
  "Create a dashboard from all uploaded files."
];

export function ChatPanel({ disabled, onAsk }: Props) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  async function submit(question: string) {
    if (!question.trim()) return;
    setLoading(true);
    setMessages((current) => [...current, { role: "user", content: question }]);
    setInput("");
    try {
      const response = await onAsk(question);
      setMessages((current) => [...current, { role: "assistant", content: response.answer, response }]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    void submit(input);
  }

  return (
    <main className="flex min-h-0 flex-col bg-background">
      <div className="flex-1 overflow-y-auto px-5 py-5">
        {!messages.length && (
          <div className="mx-auto max-w-3xl">
            <div className="mb-4 flex items-center gap-2 text-primary">
              <Sparkles size={18} />
              <span className="text-sm font-semibold">Ask the analyst</span>
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  className="rounded-md border border-border bg-white px-4 py-3 text-left text-sm hover:border-primary"
                  disabled={disabled}
                  onClick={() => void submit(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="mx-auto max-w-3xl space-y-4">
          {messages.map((message, index) => (
            <article
              key={index}
              className={message.role === "user" ? "ml-auto max-w-2xl rounded-md bg-primary px-4 py-3 text-white" : "rounded-md border border-border bg-white px-4 py-3"}
            >
              <p className="whitespace-pre-wrap text-sm leading-6">{message.content}</p>
              {message.response?.chart && <ChartRenderer chart={message.response.chart} />}
              {message.response?.reasoning.length ? (
                <div className="mt-4 border-t border-border pt-3">
                  <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Reasoning</h4>
                  <ol className="mt-2 list-decimal space-y-1 pl-5 text-sm text-slate-700">
                    {message.response.reasoning.map((step) => (
                      <li key={step}>{step}</li>
                    ))}
                  </ol>
                </div>
              ) : null}
              {message.response?.sql && <CodeBlock title="SQL" code={message.response.sql} />}
              {message.response?.generated_code && <CodeBlock title="Pandas" code={message.response.generated_code} />}
              {message.response?.anomalies.length ? (
                <pre className="mt-3 max-h-52 overflow-auto rounded-md bg-slate-950 p-3 text-xs text-slate-100">
                  {JSON.stringify(message.response.anomalies, null, 2)}
                </pre>
              ) : null}
            </article>
          ))}
        </div>
      </div>
      <form onSubmit={handleSubmit} className="border-t border-border bg-white p-4">
        <div className="mx-auto flex max-w-3xl gap-2">
          <input
            className="h-11 flex-1 rounded-md border border-border px-3 text-sm outline-none focus:border-primary"
            disabled={disabled || loading}
            placeholder={disabled ? "Upload CSV files to start" : "Ask about revenue, trends, anomalies, SQL..."}
            value={input}
            onChange={(event) => setInput(event.target.value)}
          />
          <Button disabled={disabled || loading || !input.trim()} aria-label="Send question">
            <Send size={16} />
            {loading ? "Thinking" : "Send"}
          </Button>
        </div>
      </form>
    </main>
  );
}

function CodeBlock({ title, code }: { title: string; code: string }) {
  return (
    <div className="mt-3">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</h4>
      <pre className="mt-2 overflow-x-auto rounded-md bg-slate-950 p-3 text-xs text-slate-100">
        <code>{code}</code>
      </pre>
    </div>
  );
}
