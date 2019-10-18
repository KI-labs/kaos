from graphviz import Digraph

from kaos_backend.constants import BUILD_SERVE_PIPELINE_PREFIX, \
    BUILD_TRAIN_PIPELINE_PREFIX, TRAIN_DATA_REPO_PREFIX, \
    SERVE_SOURCE_REPO_PREFIX, TRAIN_IMAGE_REPO_PREFIX, \
    TRAIN_PIPELINE_PREFIX, TRAIN_SOURCE_REPO_PREFIX, MODEL_REPO_PREFIX, \
    HYPER_REPO_PREFIX, SERVE_IMAGE_REPO_PREFIX

from kaos_model.common import ModelInfo, ServeInfo, PartitionInfo


def build_model_provenance_dag(workspace: str,
                               model_info: ModelInfo,
                               model_provenance: PartitionInfo):

    hyperparams = model_provenance.hyperparams
    dot = Digraph()

    # label DAG
    dot.attr(label=rf"<<font point-size='8'>"
                   rf"<font color='blue'><b>{model_info.path}</b></font><br/>"
                   rf"<font color='red'><b>{model_info.commit_id}</b></font></font><br/>"
                   rf"<font point-size='14'>"
                   rf"<br/><br/>Trained model with <b>kaos</b></font><br/><br/>"
                   rf"<font point-size='12'>"
                   rf"{model_info.user}<br/>"
                   rf"{model_info.created_at}<br/></font>>")
    dot.attr(compound='true', overlap='false')

    # define nodes
    node_fs = '12'
    dot.node('1', f"{TRAIN_SOURCE_REPO_PREFIX}-{workspace}", shape='cylinder', style='filled', fillcolor='lightgrey',
             color='slategrey',
             fontsize=node_fs)
    dot.node('2', f"{BUILD_TRAIN_PIPELINE_PREFIX}-{workspace}", shape='egg', fontsize=node_fs)
    dot.node('3', f"{TRAIN_IMAGE_REPO_PREFIX}-{workspace}", shape='cylinder', style='filled', fillcolor='lightgrey',
             color='slategrey',
             fontsize=node_fs)
    dot.node('4', f"{TRAIN_DATA_REPO_PREFIX}-{workspace}", shape='cylinder', style='filled', fillcolor='lightgrey',
             color='slategrey',
             fontsize=node_fs)
    dot.node('5', f"{TRAIN_PIPELINE_PREFIX}-{workspace}", shape='egg', fontsize=node_fs)
    dot.node('6', f"{MODEL_REPO_PREFIX}-{workspace}", shape='cylinder', style='filled', fillcolor='lightgrey',
             color='slategrey',
             fontsize=node_fs)

    if hyperparams:
        dot.node('100', f"{HYPER_REPO_PREFIX}-{workspace}", shape='cylinder', style='filled',
                 fillcolor='lightgrey',
                 color='slategrey',
                 fontsize=node_fs)

    # define edges
    spacer = '    '
    minlen = '1'
    label_fs = '8'
    code = model_provenance.code
    dot.edge('1', '2', taillabel=f"{spacer}{code.path}{spacer}",
             label=f"{spacer}{code.commit}{spacer}",
             fontsize=label_fs, fontcolor='red', labelfontcolor='blue', splines='True', minlen=minlen)
    data = model_provenance.data
    dot.edge('2', '3', taillabel="", splines='True', minlen=minlen)
    dot.edge('4', '5', taillabel=f"{spacer}{data.path}{spacer}",
             label=f"{spacer}{data.commit}{spacer}",
             fontsize=label_fs, fontcolor='red', labelfontcolor='blue', splines='True', minlen=minlen)
    image = model_provenance.image
    dot.edge('3', '5', taillabel=f"{spacer}{image.path}{spacer}",
             label=f"{spacer}{image.commit}{spacer}",
             fontsize=label_fs, fontcolor='red', labelfontcolor='blue', splines='True', minlen=minlen)
    dot.edge('5', '6', taillabel="", splines='True', minlen=minlen)

    if hyperparams:
        dot.edge('100', '5', taillabel=f"{spacer}{hyperparams.path}{spacer}",
                 label=f"{spacer}{hyperparams.commit}{spacer}",
                 fontsize=label_fs, fontcolor='red', labelfontcolor='blue', splines='True', minlen=minlen)

    return dot


def build_endpoint_provenance_dag(workspace: str,
                                  endpoint_description: ServeInfo,
                                  model_dag=None):

    dot = model_dag if model_dag else Digraph()

    # label DAG
    dot.attr(label=rf"<<font point-size='8'>"
                   rf"<font color='blue'><b>{endpoint_description.url}</b></font></font><br/>"
                   rf"<font point-size='14'>"
                   rf"<br/><br/>Served model with <b>kaos</b></font><br/><br/>"
                   rf"<font point-size='12'>"
                   rf"{endpoint_description.user}<br/>"
                   rf"{endpoint_description.created_at}<br/></font>>")
    dot.attr(compound='true', overlap='false')

    # define nodes
    node_fs = '12'
    dot.node('6', f"{MODEL_REPO_PREFIX}-{workspace}", shape='cylinder', style='filled', fillcolor='lightgrey',
             color='slategrey', fontsize=node_fs)
    dot.node('7', f"{SERVE_SOURCE_REPO_PREFIX}-{workspace}", shape='cylinder', style='filled', fillcolor='lightgrey',
             color='slategrey', fontsize=node_fs)
    dot.node('8', f"{BUILD_SERVE_PIPELINE_PREFIX}-{workspace}", shape='egg', fontsize=node_fs)
    dot.node('9', f"{SERVE_IMAGE_REPO_PREFIX}-{workspace}", shape='cylinder', style='filled', fillcolor='lightgrey',
             color='slategrey', fontsize=node_fs)
    dot.node('10', endpoint_description.name, shape='egg', fontsize=node_fs)
    dot.node('11', "endpoint", shape='egg', style='filled', fillcolor='indianred2', color='black', fontsize=node_fs)

    # define edges
    spacer = '    '
    minlen = '1'
    label_fs = '8'

    model = endpoint_description.model
    dot.edge('6', '8', taillabel=f"{spacer}{model.model_id}{spacer}",
             label=f"{spacer}{model.commit_id}{spacer}",
             fontsize=label_fs, fontcolor='red', labelfontcolor='blue', splines='True', minlen=minlen)
    code = endpoint_description.code
    dot.edge('7', '8', taillabel=f"{spacer}{code.path}{spacer}",
             label=f"{spacer}{code.commit}{spacer}",
             fontsize=label_fs, fontcolor='red', labelfontcolor='blue', splines='True', minlen=minlen)
    dot.edge('8', '9', taillabel="", splines='True', minlen=minlen)
    image = endpoint_description.image
    dot.edge('9', '10', taillabel=f"{spacer}{image.path}{spacer}",
             label=f"{spacer}{image.commit}{spacer}",
             fontsize=label_fs, fontcolor='red', labelfontcolor='blue', splines='True', minlen=minlen)
    dot.edge('10', '11', taillabel="", splines='True', minlen=minlen)

    return dot


def build_full_provenance_dag(workspace: str,
                              pipeline_info: ServeInfo,
                              model_provenance: PartitionInfo):

    model_dag = build_model_provenance_dag(workspace,
                                           pipeline_info.model,
                                           model_provenance)

    full_dag = build_endpoint_provenance_dag(workspace,
                                             pipeline_info,
                                             model_dag)

    return full_dag
