import React from "react";

const URL_REGEX = /(https?:\/\/[^\s]+)/g;
const URL_CHECK = /^https?:\/\/[^\s]+$/;

export function renderTextWithLinks(text: string) {
  const parts = text.split(URL_REGEX);

  return parts.map((part, i) => {
    if (URL_CHECK.test(part)) {
      return (
        <a
          key={i}
          href={part}
          target="_blank"
          rel="noopener noreferrer"
        >
          {part}
        </a>
      );
    }

    return <React.Fragment key={i}>{part}</React.Fragment>;
  });
}