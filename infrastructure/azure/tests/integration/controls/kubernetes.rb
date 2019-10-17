# encoding: utf-8
# copyright: 2018, The Authors

title "Kubernetes"
describe "Testing the K8s module"

env = ENV["ENVIRONMENT"]

control 'TF Kubernetes' do
    ## Assert that the Resource Group Exists
  describe azurerm_resource_groups do
    its('names') { should include "kaos-2-#{env}-k8s" }
  end

  ### Test that a Resource Group has the named AKS Cluster
  describe azurerm_aks_clusters(resource_group: "kaos-2-#{env}-k8s") do
    its('names') { should include("kaos-2-#{env}-k8s") }
  end

  # Insist that Vnet exists
  describe azurerm_virtual_networks(resource_group: "kaos-2-#{env}-k8s")
    .where(name: 'kaos-2-stage-vnet') do
    it { should exist }
  end

  # Insist that MySubnet exists
  describe azurerm_subnets(resource_group: "kaos-2-#{env}-k8s", vnet: "kaos-2-#{env}-vnet")
    .where(name: "kaos-2-#{env}-k8s-subnet") do
    it { should exist }
  end
end
