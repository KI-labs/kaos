import prettytable
from kaos_model.api import PagedResponse
from kaos_model.common import JobInfo
from prettytable import PrettyTable


def render_table(data, header=None, include_ind=True, drop_cols: set = None):
    if not drop_cols:
        drop_cols = set()

    for d in data:
        for k in list(d):
            if k in drop_cols:
                del d[k]

    # set up simple table to iterate through response
    table = PrettyTable(hrules=prettytable.ALL)
    if header:
        table.title = header
    out = list(data)

    if include_ind:
        table.field_names = ['ind'] + list(out[0].keys())
        for ind, d in enumerate(out):
            table.add_row([ind] + list(d.values()))
    else:
        table.field_names = list(out[0].keys())
        for d in out:
            table.add_row(list(d.values()))
    return table.get_string()


def render_queued_table(building_jobs, header, include_ind=True, drop_cols=None):
    last_option = list(
        sorted(
            building_jobs,
            key=lambda x: x['started'],
            reverse=True)
    )[:1]

    if last_option and last_option[0]['state'] in ("JOB_RUNNING", "JOB_FAILURE"):
        return f"\n{render_table(last_option, header, include_ind=include_ind, drop_cols=drop_cols)}\n", 1
    else:
        return "", 0


def render_job_info(data, sort_by):
    response = PagedResponse.from_dict(data)
    info = JobInfo.from_dict(response.response)
    page_id = response.page_id
    page_count = response.page_count
    # "global" (i.e. job) level info
    formatted_info = f"""
    Job ID: {info.job_id}
    Process time: {info.process_time}
    State: {info.state}
    Available metrics: {info.available_metrics}

    Page count: {page_count}
    Page ID: {page_id}"""
    table = PrettyTable(hrules=prettytable.ALL)
    header = ['ind', 'Code', 'Data', 'Model ID', 'Hyperparams']
    if sort_by:
        header.append('Score')
    table.field_names = header
    for ind, d in enumerate(info.partitions):
        code = d.code
        code_summary = f"Author: {code.author}\nPath: {code.path}"

        data = d.data
        data_summary = f"Author: {data.author}\nPath: {data.path}"

        hyper_summary = None
        if d.hyperparams:
            hyper = d.hyperparams
            hyper_summary = f"Author: {hyper.author}\nPath: {hyper.path}"

        output = d.output
        output_summary = f"{output.path}"
        row = [ind, code_summary, data_summary, output_summary, hyper_summary]
        if sort_by:
            row.append(d.score)
        table.add_row(row)
    formatted_info += "\n" + table.get_string()
    return formatted_info
