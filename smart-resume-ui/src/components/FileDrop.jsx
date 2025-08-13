import { useRef, useState } from "react";

export default function FileDrop({ label, accept, onFile }) {
  const [name, setName] = useState("");
  const inputRef = useRef(null);

  function onSelect(file) {
    if (!file) return;
    setName(`${file.name} (${Math.round(file.size / 1024)} KB)`);
    onFile(file);
  }

  return (
    <div
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        const f = e.dataTransfer.files?.[0];
        onSelect(f);
      }}
      onClick={() => inputRef.current?.click()}
      className="drop"
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
      title="Click or drop a file"
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: "none" }}
        onChange={(e) => onSelect(e.target.files?.[0])}
      />
      <div className="drop-title">{label}</div>
      <div className="drop-sub">
        Drag & drop or <span className="link">browse</span>
      </div>
      {name && <div className="drop-name">{name}</div>}
    </div>
  );
}
