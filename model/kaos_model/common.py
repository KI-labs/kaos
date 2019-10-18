from dataclasses import dataclass
from dataclasses_json import dataclass_json

from typing import List, Optional


@dataclass_json
@dataclass
class WorkspaceInfo:
    name: str
    pipelines: List[str]
    repos: List[str]


@dataclass_json
@dataclass
class DataDescriptor:
    repo: str
    commit: str
    path: str
    branch: str = "master"
    author: Optional[str] = None


@dataclass_json
@dataclass
class PartitionInfo:
    datum_id: str
    code: DataDescriptor
    data: DataDescriptor
    image: DataDescriptor
    output: DataDescriptor
    score: Optional[str] = None
    hyperparams: Optional[DataDescriptor] = None


@dataclass_json
@dataclass
class SubmissionInfo:
    """
    Represents a queued job.
    """
    job_id: str
    state: str
    started: str
    duration: int
    progress: str
    hyperopt: Optional[str] = None


@dataclass_json
@dataclass
class JobInfo:
    """
    Represents a running, completed or failed  training job.
    """
    job_id: str
    state: str
    available_metrics: List[str]
    process_time: int
    partitions: List[PartitionInfo]


@dataclass_json
@dataclass
class ModelInfo:
    user: str
    commit_id: str
    size: str
    path: str
    base_path: str
    model_id: str
    created_at: str


@dataclass_json
@dataclass
class ServeInfo:
    name: str
    url: str
    user: str
    state: str
    created_at: str
    code: Optional[DataDescriptor] = None
    image: Optional[DataDescriptor] = None
    model: Optional[ModelInfo] = None


@dataclass_json
@dataclass
class TrainJobListing:
    training: List[SubmissionInfo]
    building: List[SubmissionInfo]
    ingesting: List[SubmissionInfo]
