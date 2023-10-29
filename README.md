# Why
When tasked to create a new report, as a military officer, the report must adhere to the army's guidelines and specifications. Having to create a new report usually means opening a similar previous report and editing some data in it. This is the easy way to do it, **but** when you are tasked to create a new report from scratch then things get rough. Having to apply the army's guidelines and specifications to the document when working with your usual document processor (eg Word) can be very cumbersome. Most of your time is comsumed editing the documents layout and aligning text, when it should be focusing on the content. This tool automates the "layout" part of the process and more. When dealing with huge documents ranging from 30 all the way to 200 pages (it can happen), the usual workflow is splitting the document to many folders and files. This creates a large tree of folders and files that is very difficult to handle. Another important aspect of army documents is the repetion of certain fields or data. When having an large number of files for a single final document you have to manually open and edit each and every file that contains repetitive data that changed (eg. date). Another problem is headers, footers and page numbering. The army follows a specific scheme for all these and implementing those in Word for example is possible but very time consuming and one needs to know their tool (Word) to do it effectively. All these lead to errors, inconsistencies, lost work hours and the document writer gets exhausted.

# How
This tool abstracts everything and the user has to think only about the document's content and nothing more. Given and text file with simple instructions in it, the user get a pdf file with proper pagination, consistent data across the whole document and in a fraction of the time.

# Example Case
Imagine you have a 200 page document. In the army you first create a draft. The draft gets passed from the handler to his superiors and corrections are made on paper. After that the handler edits the document, gets ids for it and the creates a final pdf called exact copy. This exact copy can then be print or sent by email.

First of all, being a 200 page document, this usually means 10-15 folders with 3-5 files each one. Each file might be multiple pages. A common practice is to split a huge document to parts and subparts. All these share the same date, document id and/or other data (eg. the handler).

Manually creating the draft will take 'X' time. The problem is that after the first few corrections or edits from the superiors the process becomes the following.
check files affected by changes -> open every file -> edit -> save -> pass draft to superiors for further changes.

After the draft -> pass to superiors -> reprint draft ends, the handlers gets the documents ids and applies them to all affected files and also changes specific parts that convert the draft to an exact copy. This process can mean up to 30 files opened-edited-saved as pdf. In the end the handler combines all pdf files to the final pdf document and prints/sends it. 

With this tool he would just create the initial draft. Run the tool and get a draft pdf to print. Pass the draft to the superiors and after each change, he would edit the specific lines and variables in the document. Run the draft through the tool again and get his new draft or if done, his final document as a pdf for print/send.
