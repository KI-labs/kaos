# Killing a training job

Whenever your training submission is getting stuck at either building or training stage, you can kill it with a `kaos train kill` command.

```
$ kaos train list

+--------------------------------------------------------------------------------------------+
|                                          BUILDING                                          |
+----------+----------+----------------------------------+---------------------+-------------+
| duration | hyperopt |              job_id              |       started       |    state    |
+----------+----------+----------------------------------+---------------------+-------------+
|    ?     |   None   | 372d7390d7994777a7df589ac8a93c18 | 2019-09-19 11:49:33 | JOB_RUNNING |
+----------+----------+----------------------------------+---------------------+-------------+

$ kaos train kill -j 372d7390d7994777a7df589ac8a93c18
Job 372d7390d7994777a7df589ac8a93c18 successfully killed

$ kaos train list
There are currently no training jobs - first run kaos train deploy
```

{% hint style="warning" %}
Note that`kaos train kill`can be only applied to **starting** or **running** building/training jobs.
{% endhint %}

If you try to delete a finished or nonexistent job, CLI will warn you:

```text
$ kaos train list

+--------------------------------------------------------------------------------------------------+
|                                             TRAINING                                             |
+-----+----------+----------+----------------------------------+---------------------+-------------+
| ind | duration | hyperopt |              job_id              |       started       |    state    |
+-----+----------+----------+----------------------------------+---------------------+-------------+
|  0  |    3     |  False   | 67dd49ad56c54247bbd81f60f01cbd07 | 2019-09-19 11:51:57 | JOB_SUCCESS |
+-----+----------+----------+----------------------------------+---------------------+-------------+

$ kaos train kill -j 67dd49ad56c54247bbd81f60f01cbd07

Job is not running, id: 67dd49ad56c54247bbd81f60f01cbd07

$ kaos train kill -j nonexistent_id                                                                                                             1 ↵

There is no job with id: nonexistent_id
```

