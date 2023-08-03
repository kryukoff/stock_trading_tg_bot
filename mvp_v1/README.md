First working prototype.

Users can select 2 roles.

Buyer - wait for messages from sellers

Seller - selects through tree-like menu item for sale, offers price, the buyer will get exact item specs, price, and seller's @username

Requires .XLSX filename with columns
serie	number	model	Memory	Color	Sim
... ... ... ... ... ... ... 

The list of items should include all possible combinations of items
after selecting first column, dataframe drops all the remaining items that do not include the selected value and so on.

