# LinkedIn-Saral-Apply

```
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```

Data Structure for Data Base:
{
    "#jobID" : {
        "link" : "#Link",
        "title" : "#Title",
        "state" : "#State",
        "companyName" : "#companyName",
        "location" : "#Location",
        "method" : "Manual/EasyApply",
        "timeStamp" : "#timeStamp",
        "applyTime" : "NoTime/applyTime",
        "status" : "Applied/NotApplied",
        "revert" : "Yes/No",
    },
}

dsv = (link, title, state, companyName, location, method, timeStamp, applyTime, status, revert)

sudo nano /etc/systemd/system/runFastAPI.service
sudo systemctl daemon-reload
sudo systemctl stop runFastAPI.service
sudo systemctl start runFastAPI.service
sudo systemctl enable runFastAPI.service
sudo systemctl status runFastAPI.service
journalctl -u runFastAPI.service -f



sudo nano /etc/systemd/system/dataScraping.service
