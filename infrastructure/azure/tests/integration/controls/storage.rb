# encoding: utf-8
# copyright: 2018, The Authors

title "Storage"
describe "Testing the storage module"

env = ENV["ENVIRONMENT"]

control 'TF Storage' do
  ## Assert that the Resource Group Exists
  describe azurerm_resource_groups do
      its('names') { should include "kaos-2-#{env}-internal-rg" }
  end

  ### Ensure that a Blob Container exists
  #describe azurerm_storage_account_blob_containers(resource_group: 'kaos-internal-rg-dev', storage_account_name: 'internal-dev-0') do
  #  it {should exist}
  #end
end