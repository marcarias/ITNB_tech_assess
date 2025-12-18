from dataclasses import dataclass

@dataclass
class PipelineConfig:
    deduplicate: bool = False
