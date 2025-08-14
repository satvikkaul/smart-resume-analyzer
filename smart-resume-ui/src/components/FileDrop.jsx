import { useState, useRef, useEffect } from "react";

export default function FileDrop({ label, accept, onFile, reset }) {
  const [name, setName] = useState("");
  const [isOver, setIsOver] = useState(false);
  const inputRef = useRef(null);

  // clear on reset trigger
  useEffect(() => {
    setName("");
    if (inputRef.current) inputRef.current.value = "";
  }, [reset]);

  const allowed = (accept || "").split(",").map(s => s.trim().toLowerCase());
  const isAllowed = (file) =>
    !!file && allowed.some(ext => file.name.toLowerCase().endsWith(ext));

  const onSelect = (file) => {
    if (!file) return;
    setName(`${file.name} (${Math.round(file.size / 1024)} KB)`);
    onFile?.(file);
  };

  return (
    <div
      className={`drop ${isOver ? "over" : ""}`}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setIsOver(true); }}
      onDragEnter={() => setIsOver(true)}
      onDragLeave={() => setIsOver(false)}
      onDrop={(e) => {
        e.preventDefault(); setIsOver(false);
        const f = e.dataTransfer.files?.[0];
        if (!isAllowed(f)) return;
        onSelect(f);
      }}
      title="Click or drop a file"
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: "none" }}
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (!isAllowed(f)) return;
          onSelect(f);
        }}
      />
      <div className="drop-title">{label}</div>
      <div className="drop-sub">Drag & drop or <span className="link">browse</span></div>
      {name && <div className="drop-name">{name}</div>}
    </div>
  );
}
