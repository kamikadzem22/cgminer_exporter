import datetime
def metric_pool(data, tags):
	string = "# Pools Data\n"
	string += "cgminer_pool_count{%s} %s\n"%(tags, len(data['POOLS']))
	for pool in data['POOLS']:
		localtags = 'pool="%s",url="%s",stratum_url="%s",%s'%(pool['POOL'], pool['URL'], pool['Stratum URL'], tags)
		string += 'cgminer_pool_diff_accepted{%s} %s\n'%(localtags, pool['Difficulty Accepted'])
		string += 'cgminer_pool_rejected{%s} %s\n'%(localtags, pool['Difficulty Accepted'])
		string += 'cgminer_pool_diff_rejected{%s} %s\n'%(localtags, pool['Difficulty Rejected'])
		string += 'cgminer_pool_stale{%s} %s\n'%(localtags, pool['Stale'])
		try:
			[hr, mn, ss] = [int(x) for x in pool['Last Share Time'].split(':')]
			sharetime = datetime.timedelta(hours=hr, minutes=mn, seconds=ss).seconds
		except:
			sharetime = 0
		string += 'cgminer_pool_last_share{%s} %s\n'%(localtags, sharetime)
		string += 'cgminer_pool_getworks{%s} %s\n'%(localtags, pool['Getworks'])
		string += 'cgminer_pool_last_diff{%s} %s\n'%(localtags, pool['Last Share Difficulty'])
		if pool['Status'] == "Alive":
			status = 1
		else:
			status = 0
		string += 'cgminer_pool_status{%s} %s\n'%(localtags, status)
		if pool['Stratum Active']:
			active = 1
		else:
			active = 0
		string += 'cgminer_pool_stratum_active{%s} %s\n'%(localtags, active)
	return (string)

def metric_summary(data, tags):
	string = "#Pool Summary\n"
	localtags = tags
	string += 'cgminer_summary_rejected{%s} %s\n'%(localtags, data['SUMMARY'][0]['Rejected'])
	string += 'cgminer_summary_found_blocks{%s} %s\n'%(localtags, data['SUMMARY'][0]['Found Blocks'])
	string += 'cgminer_summary_elapsed{%s} %s\n'%(localtags, data['SUMMARY'][0]['Elapsed'])
	string += 'cgminer_summary_hardware_errors{%s} %s\n'%(localtags, data['SUMMARY'][0]['Hardware Errors'])
	string += 'cgminer_summary_total_mh{%s} %s\n'%(localtags, data['SUMMARY'][0]['Total MH'])
	string += 'cgminer_summary_ghs_average{%s} %s\n'%(localtags, data['SUMMARY'][0]['GHS av'])
	string += 'cgminer_summary_ghs_5s{%s} %s\n'%(localtags, data['SUMMARY'][0]['GHS 5s'])

	return (string)

def metric_stats(data, tags):
	string = "# Stats\n"
	statdata = data['STATS'][1]
	localtags = '%s'%(tags)
	for entry in statdata:
		if 'temp' in entry:
			tempnum = entry.replace("temp","")
			string += 'cgminer_stats_temp{temp="%s",%s} %s\n'%(tempnum, localtags, statdata['temp%s'%(tempnum)])
		if 'chain_hw' in entry:
			chainnum = entry.replace("chain_hw","")
			if statdata['chain_rate%s'%(chainnum)]:
				string += 'cgminer_stats_chain_rate{chain="%s",%s} %s\n'%(chainnum, localtags, statdata['chain_rate%s'%(chainnum)])
			else:
				string += 'cgminer_stats_chain_rate{chain="%s",%s} %s\n'%(chainnum, localtags, 0)
			string += 'cgminer_stats_chain_acn{chain="%s",%s} %s\n'%(chainnum, localtags, statdata['chain_acn%s'%(chainnum)])
			string += 'cgminer_stats_chain_hw{chain="%s",%s} %s\n'%(chainnum, localtags, statdata['chain_hw%s'%(chainnum)])
		if 'fan' in entry and entry != "manual_fan_mode":
			fannum = entry.replace("fan","")
			string += 'cgminer_stats_fan{fan="%s",%s} %s\n'%(fannum, localtags, statdata['fan%s'%(fannum)])
		if 'freq_avg' in entry:
			freqnum = entry.replace("freq_avg","")
			string += 'cgminer_stats_freq{freq="%s",%s} %s\n'%(freqnum, localtags, statdata['freq_avg%s'%(freqnum)])

	string += 'cgminer_stats_frequency{%s} %s\n'%(localtags, statdata['frequency'])

	return (string)