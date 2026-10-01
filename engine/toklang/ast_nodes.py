"""
TokLang AST Nodes & Typed Grammar Structures (TokLang Core Engine)
Define os nos sintaticos da arvore abstrata de compilacao do TokLang.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ASTNode:
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class CompressionDirective(ASTNode):
    level: str = "balanced"  # lossless, balanced, aggressive
    target: str = "semantic"
    drop_stopwords: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "compression_directive",
            "level": self.level,
            "target": self.target,
            "drop_stopwords": self.drop_stopwords
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CompressionDirective":
        return cls(
            level=d.get("level", "balanced"),
            target=d.get("target", "semantic"),
            drop_stopwords=d.get("drop_stopwords", True)
        )


@dataclass
class TokenBudgetDirective(ASTNode):
    max_tokens: int = 1000
    reserve_completion: int = 250

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "budget_directive",
            "max_tokens": self.max_tokens,
            "reserve_completion": self.reserve_completion
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TokenBudgetDirective":
        return cls(
            max_tokens=d.get("max_tokens", 1000),
            reserve_completion=d.get("reserve_completion", 250)
        )


@dataclass
class AttentionConstraint(ASTNode):
    name: str
    focus_terms: list[str] = field(default_factory=list)
    strictly_inviolable: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "attention_constraint",
            "name": self.name,
            "focus_terms": self.focus_terms,
            "strictly_inviolable": self.strictly_inviolable
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "AttentionConstraint":
        return cls(
            name=d.get("name", "unnamed"),
            focus_terms=d.get("focus_terms", []),
            strictly_inviolable=d.get("strictly_inviolable", True)
        )


@dataclass
class ContextBlock(ASTNode):
    name: str
    content: str
    priority: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "context_block",
            "name": self.name,
            "content": self.content,
            "priority": self.priority
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ContextBlock":
        return cls(
            name=d.get("name", ""),
            content=d.get("content", ""),
            priority=d.get("priority", 1)
        )


@dataclass
class InstructionBlock(ASTNode):
    instructions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "instruction_block",
            "instructions": self.instructions
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "InstructionBlock":
        return cls(instructions=d.get("instructions", []))


@dataclass
class PromptDocument(ASTNode):
    name: str = "main"
    compression: CompressionDirective | None = None
    budget: TokenBudgetDirective | None = None
    constraints: list[AttentionConstraint] = field(default_factory=list)
    contexts: list[ContextBlock] = field(default_factory=list)
    instruction: InstructionBlock | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "prompt_document",
            "name": self.name,
            "compression": self.compression.to_dict() if self.compression else None,
            "budget": self.budget.to_dict() if self.budget else None,
            "constraints": [c.to_dict() for c in self.constraints],
            "contexts": [c.to_dict() for c in self.contexts],
            "instruction": self.instruction.to_dict() if self.instruction else None
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PromptDocument":
        doc = cls(name=d.get("name", "main"))
        if d.get("compression"):
            doc.compression = CompressionDirective.from_dict(d["compression"])
        if d.get("budget"):
            doc.budget = TokenBudgetDirective.from_dict(d["budget"])
        doc.constraints = [AttentionConstraint.from_dict(c) for c in d.get("constraints", [])]
        doc.contexts = [ContextBlock.from_dict(c) for c in d.get("contexts", [])]
        if d.get("instruction"):
            doc.instruction = InstructionBlock.from_dict(d["instruction"])
        return doc
