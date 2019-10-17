locals {
  cpu_counts = [
    for n in split(" ", data.external.resources.result.cpu) :
    tonumber(n)
  ]
  memory_counts = [
    for n in split(" ", data.external.resources.result.memory) :
    tonumber(n)
  ]
  gpu_counts = [
    for n in split(" ", data.external.resources.result.gpu) :
    tonumber(n)
  ]
}