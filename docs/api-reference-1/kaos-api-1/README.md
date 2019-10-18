# Application Structure

The application is divided into **four** layers.

## Module `routes`

The outermost layer that specifies the REST API of the backend and leaves all the processing to`controllers`. It handles everything HTTP-specific, marshals exceptions into responses.

| Route | Purpose |
| :--- | :--- |
| [/workspace](workspace.md) | create separate ML environments within kaos |
| [/notebook](notebook.md) | create a hosted Jupyter notebook with kaos |
| [/data](kaos-api.md) | upload datasets for usage within kaos |
| [/train](train.md) | deploy training\(s\) based on source code, data and parameters |
| [/inference](inference.md) | deploy an endpoint with a trained model |
| [/internal](internal.md) | callback for deploying pipelines |

## Module `controllers`

It contains all the high-level business logic of the application.

## Module `services`

It encapsulates all low-level mechanics and exposes an abstracted interface, so that the controllers manipulate with kaos-specific concepts without any low-level logic.

## Module `clients`

A thin wrapper over [Pachyderm](https://pachyderm.io/) internal storage and pipeline clients. It organizes access to Pachyderms' subsystems, decodes the responses and provides error handling.

