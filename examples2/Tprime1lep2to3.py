from TIMBER.Analyzer import *
from TIMBER.Tools.Common import *

import ROOT
from ROOT import TFile
import sys, os

from TIMBER.Tools.RestFramesHandler import load_restframes

# From https://gist.github.com/pieterdavid/a560e65658386d70a1720cb5afe4d3e9#file-df-py  example
import correctionlib
correctionlib.register_pyroot_binding()

sys.path.append('../../')
sys.path.append('../../../')

# ------------------ Command Line Arguments and Parsing -------------------
inputFiles = sys.argv[1] #fileList
testNum1 = sys.argv[2]
testNum2 = sys.argv[3]
campaign = sys.argv[4]  #switched the argument from campaign back to year.

             #---------- Argument dependent Variables ---------
if (campaign == "Summer22"): year = "2022";

elif (campaign == "Summer22EE"): year = "2022";

elif (campaign == "Summer23"): year = "2023";

elif (campaign == "Summer23BPix"): year = "2023";

#selfDerived_corr.cc --> replace year block with 2022/2023 corrections?
else: print(f'ERROR: Can\'t parse the RUN 3 campaign (Argument 4). Expected Summer22, Summer22EE, Summer23, or Summer23BPix. Got: {campaign}\n')

# Make the New .txt file from line testNum1 to testNum2 because TIMBER can handle .txt of .root's files
print(f"Input File Path: {inputFiles}")
with open(inputFiles) as fp:
	lines = fp.readlines()

start = int(testNum1)
end = int(testNum2)

print(f"TestNum 1: {start} and TestNum 2: {end}")

listFiles = open('trimmed_input.txt', 'w')
  #if (listFiles.is_open())
for i, line in enumerate(lines): #, start=1):
	if i in [start, end]:
		listFiles.write(line)
listFiles.close()

print(f"Number of Entries: {end - start}")
sampleName = lines[start]
print(f"Sample Name: {sampleName}")
os.system("cat trimmed_input.txt")

# Parse the incoming file names to assign labels
isSig = ("Bprime" in sampleName)
isMadgraphBkg = (("QCD" in sampleName) or ("madgraphMLM" in sampleName))
isTOP = (("Mtt" in sampleName) or ("ST" in sampleName) or ("ttZ" in sampleName) or ("ttW" in sampleName) or ("ttH" in sampleName) or ("TTto" in sampleName))
isTT = (("TT_Tune" in sampleName) or ("Mtt" in sampleName) or ("TTto" in sampleName)) #changed "TTTo" to "TTto" as per sample files I saw. May or may not be right?
isVV = (("WW_" in sampleName) or ("WZ_" in sampleName) or ("ZZ_" in sampleName))
isSM = ("SingleMuon" in sampleName)
isSE = (("SingleElectron" in sampleName) or ("EGamma" in sampleName))
isMC = not (("Single" in sampleName) or ("Data18" in sampleName) or ("EGamma" in sampleName))

if (isTT): samplebin = 0
elif (("ST_" in sampleName)): samplebin = 1
elif (("TTW" in sampleName) or ("TTZ" in sampleName) or ("ttH" in sampleName)): samplebin = 2
elif (("WJetsToLNu" in sampleName)): samplebin = 3
elif (("DYJets" in sampleName)): samplebin = 4
elif (isVV): samplebin = 5
elif (("QCD" in sampleName)): samplebin = 6
elif (isSig):
	if (("M-800" in sampleName)): samplebin = 7
	if (("M-1000" in sampleName)): samplebin = 8
	if (("M-1200" in sampleName)): samplebin = 9
	if (("M-1300" in sampleName)): samplebin = 10
	if (("M-1400" in sampleName)): samplebin = 11
	if (("M-1500" in sampleName)): samplebin = 12
	if (("M-1600" in sampleName)): samplebin = 13
	if (("M-1700" in sampleName)): samplebin = 14
	if (("M-1800" in sampleName)): samplebin = 15
	if (("M-2000" in sampleName)): samplebin = 16
	if (("M-2200" in sampleName)): samplebin = 17


tokens = sampleName.split("/")
sample = tokens[7] # was 5

if not isMC: 
	runera = tokens[6] # was 4
	process = tokens[9] # was 7
	dataera = runera[-1] # last char (E,F,G)
	procver = process[-5:-4] #version "before" v1, meaningless for 2022-- gives me the "version" from 1 to 4 (I think).
	if not ("v" in procver): procver = process[-2:]

if isMC:
  #Do these exist????
	if (("_ext1" in sampleName)): dataera = "ext1"
	elif (("_ext2" in sampleName)): dataera = "ext2"
	elif (("_ext3" in sampleName)): dataera = "ext3"
	else: dataera = ""
	procver = ""

era = str(dataera)

jercrunver = procver
if not (jercrunver == "v4"): jercrunver = "v123"

del tokens

# ------------------ TIMBER Analyzer inputs ------------------
num_threads = 1
#file_name = 'root://cmsxrootd.fnal.gov//store/mc/RunIISummer20UL18NanoAODv9/TprimeTprime_M-1500_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/40000/447AD74F-034B-FA42-AD05-CD476A98C43D.root'
#file_name = 'ourtestfile.root'
#file_name = 'root://cms-xrd-global.cern.ch//store/data/Run2018A/SingleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9-v2/2550000/28FF17A8-95EB-FD41-A55B-2EFAF2D6AF91.root' 
file_name = 'trimmed_input.txt'

# Import the C++
CompileCpp('TIMBER/Framework/include/common.h') # Compile (via gInterpreter) commonly used c++ code
CompileCpp('TIMBER/Framework/Tprime1lep/cleanjet.cc') # Compile Our vlq c++ code
CompileCpp('TIMBER/Framework/Tprime1lep/utilities.cc') # Compile Our vlq c++ code
CompileCpp('TIMBER/Framework/Tprime1lep/lumiMask.cc')
CompileCpp('TIMBER/Framework/Tprime1lep/selfDerived_corrs.cc')
CompileCpp('TIMBER/Framework/Tprime1lep/corr_funcs.cc') 
CompileCpp('TIMBER/Framework/Tprime1lep/generatorInfo.cc')
ROOT.gInterpreter.ProcessLine('#include "TString.h"')

handler_name = 'Tprime_handler.cc'
class_name = 'Tprime_RestFrames_Container'

# Enable using 4 threads
ROOT.ROOT.EnableImplicitMT(num_threads)

# load rest frames handler
load_restframes(num_threads, handler_name, class_name, 'rfc')

# ------------------ Important Variables ------------------
debug = True
#isData = False
#if (("Single" in inputFiles) or ("EGamma" in inputFiles)): isData = True

ROOT.gInterpreter.Declare("""
	string year = \"""" + year + """\"; 
	string sample = \"""" + sample + """\";
	string era = \"""" + era + """\";
	string dataera = \"""" + dataera + """\";
	string procver = \"""" + procver + """\";
	string jercrunver = \"""" + jercrunver + """\";
	string campaign = \"""" + campaign + """\";

	bool isMC = """+str(isMC).lower()+"""; 
	bool debug = """+str(debug).lower()+"""; 
""")


# ------------------ Analyze Function ------------------
def analyze(jesvar):
	ROOT.gInterpreter.ProcessLine('string jesvar = "' + jesvar + '"; ')

	a = analyzer(file_name) # Create analyzer instance

	print('==========================INITIALIZED ANALYZER========================')

  # ------------------ Golden JSON Data ------------------
  # change the jsonfile path to somewhere they have it in TIMBER
	jsonfile = "../TIMBER/data/LumiJSON/"

	print('========================== jsonfile = ".../LumiJSON/" ========================')
##CAMI -- add json data

	if (campaign == "Summer22" or campaign == "Summer22EE"): jsonfile = jsonfile + "Cert_Collisions2022_355100_362760_Golden.json"
	elif (campaign == "Summer23" or campaign == "Summer23BPix"): jsonfile = jsonfile + "Cert_Collisions2023_366442_370790_Golden.json"
	else: print(f'ERROR: Can\'t parse the campaign to assign a golden json file. Expected Summer22, Summer22EE, Summer23 or Summer23BPix. Got: {campaign}\n')

	print ("jason file is =", jsonfile)

	ROOT.gInterpreter.Declare("""
		const auto myLumiMask = lumiMask::fromJSON(\"""" + jsonfile + """\");
		//  std::cout << "Testing the JSON! Known good run/lumi returns: " << myLumiMask.accept(315257, 10) << ", and known bad run returns: " << myLumiMask.accept(315257, 90) << std::endl;
	""")

	print ("point b")
  #TODO more things here

     # Lepton scale factors not in correctionLib
	ROOT.gInterpreter.ProcessLine('initialize(campaign);')
# ------------------ correctionsLib corrections ------------------
	print ("point c")

	ak4pf = "_AK4PFPuppi"
	ak8pf = "_AK8PFPuppi"

	print ("point d")

### make this work for both MC and isnot MC -- MC corr names don't include version #s
	if (campaign == "Summer22"):  prompt = "Summer22_22Sep2023"; jetprompt = "Summer22_23Sep2023"; jecver = "_V2"; veto_run = "_RunCD_V1"; jercrun = "_RunCD"; mcname = str(); corrPU_name = "Collisions"+year+"_355100_357900_eraBCD_GoldenJson";
	elif (campaign == "Summer22EE"): prompt = "Summer22EE_22Sep2023"; jetprompt = "Summer22EE_23Sep2023"; jecver = "_V2"; veto_run = "_RunEFG_V1"; jercrun = "_Run"+era; mcname = str(); corrPU_name = "Collisions"+year+"_359022_362760_eraEFG_GoldenJson"; #jercrun receives a letter by era (E, F, or G). jercrun only used for actual data in 22EE so it won't interfere with processing MC.
	elif (campaign == "Summer23"): prompt = "Summer23Prompt23"; jetprompt = "Summer23Prompt23"; jecver = "_V1"; veto_run = "_RunC_V1"; jercrun = "_RunC"+jercrunver; mcname = "_RunCv1234"; corrPU_name = "Collisions"+year+"_366403_369802_eraBC_GoldenJson"; ak4pt_name = prompt + jercrun + "_JRV1_MC_PtResolution" + ak4pf; ak4jer_name = prompt + jercrun + "_JRV1_MC_ScaleFactor" + ak4pf; #jercrunver will always return v123 for isMC. Otherwise, it recognized whether data is v123 or v4 string to complete jercrun.
	elif (campaign == "Summer23BPix"): prompt = "Summer23BPixPrompt23"; jetprompt = "Summer23BPixPrompt23"; jecver = "_V1"; veto_run = "_RunD_V1"; jercrun = "_RunD"; mcname = "_RunD"; corrPU_name = "Collisions"+year+"_369803_370790_eraD_GoldenJson"; ak4pt_name = prompt + jercrun + "_JRV1_MC_PtResolution" + ak4pf; ak4jer_name = prompt + jercrun + "_JRV1_MC_ScaleFactor" + ak4pf;
	else: print(f'ERROR: Can\'t parse the campaign to assign correctionLib json files.')

	ak4pt_name = prompt + mcname + "_JRV1_MC_PtResolution" + ak4pf;
	ak4jer_name = prompt + mcname + "_JRV1_MC_ScaleFactor" + ak4pf;
#	ak8pt_name = prompt + mcname + "_JRV1_MC_PtResolution" + ak8pf;
#	ak8jer_name = prompt + mcname + "_JRV1_MC_ScaleFactor" + ak8pf;

	print ("point e")
#is it ok that I ".Declare" year & campaign twice? once in the block above "initialize" -- CAMI
	ROOT.gInterpreter.Declare("""
		string jecver = \""""+jecver+"""\";
		string jetprompt = \""""+jetprompt+"""\";
		string corrPU_name = \""""+corrPU_name+"""\";
		string mcname = \""""+mcname+"""\";
		string ak4pt_name = \""""+ak4pt_name+"""\";
		string ak4jer_name = \""""+ak4jer_name+"""\";
		string prompt = \""""+prompt+"""\";
		string ak4pf = \""""+ak4pf+"""\";
		string ak8pf = \""""+ak8pf+"""\";
		string veto_run = \""""+veto_run+"""\";
		string jercrun = \""""+jercrun+"""\";
	""")

	print ("point f")

	print ("mcname =",mcname,"\njecver =",jecver, "jetprompt =",jetprompt,"\ncorrPU_name =",corrPU_name,"\nak4pt_name (same for ak8) =",ak4pt_name,"\nak4jer_name (same for ak8) =",ak4jer_name,"\nprompt =",prompt,"\nak4pf =",ak4pf,"\nak8pf =",ak8pf,"\nveto_run =",veto_run,"\njercrun =",jercrun,"\nelectroncorrset->at(\"Electron-ID-SF\") \nmuoncorrset->at(\"NUM_MediumID_DEN_TrackerMuons\") \nmuoncorrset->at(\"NUM_Mu50_or_CascadeMu100_or_HighPtTkMu100_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose\") \njetvetocorrset->at(prompt+veto_run =",prompt+veto_run,")","\nauto ak4corrL1 = ak4corrset->at(",prompt + jercrun + jecver,"_DATA_L1FastJet",ak4pf,"\") \nauto ak4corr = ak4corrset->compound().at(",prompt + jercrun + jecver,"_DATA_L1L2L3Res",ak4pf,"\") \nak8corr = ak8corrset->compound().at(",prompt + jercrun + jecver,"_DATA_L1L2L3Res",ak8pf,")")

	print("============ point f print end ===========")
# CAMI -- in recofunc, change the muon part of the func to return value '1' instead of figuring our value from corr
# CAMI -- auto metcorrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+year+"_"+campaign+"/met.json") -- didn't find a met.json correction. Only jetvetomap, jet_jerc and fatJet_jerc
# CAMI -- check what uses metptcorr & metphicorr, change it so it returns "1"
#	auto metptcorr = metcorrset->at("pt_metphicorr_pfmet_mc");
#	auto metphicorr = metcorrset->at("phi_metphicorr_pfmet_mc");
#	if (!isMC) {
#	  metptcorr = metcorrset->at("pt_metphicorr_pfmet_data");
#	  metphicorr = metcorrset->at("phi_metphicorr_pfmet_data"); };

	ROOT.gInterpreter.Declare("""
	auto csetPU = correction::CorrectionSet::from_file("jsonpog-integration/POG/LUM/"+year+"_"+campaign+"/puWeights.json");
	auto electroncorrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/EGM/"+year+"_"+campaign+"/electron.json");
	auto muoncorrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/MUO/"+year+"_"+campaign+"/muon_HighPt.json");
	auto jetvetocorrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+year+"_"+campaign+"/jetvetomaps.json");

	auto corrPU = csetPU->at(corrPU_name);
	auto electroncorr = electroncorrset->at("Electron-ID-SF");
	auto muoncorr = muoncorrset->at("NUM_GlobalMuons_DEN_TrackerMuonProbes");
	auto muonidcorr = muoncorrset->at("NUM_TightID_DEN_GlobalMuonProbes");
	auto jetvetocorr = jetvetocorrset->at(jetprompt+veto_run);
	""")
# auto muonhltcorr = muoncorrset->at("NUM_Mu50_or_CascadeMu100_or_HighPtTkMu100_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose"); ##CAMI DO: replace places and put a placeholder that returns "1"
	print ("point g")
	if not isMC:
		ROOT.gInterpreter.Declare("""
			auto ak4corrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+year+"_"+campaign+"/jet_jerc.json");
			auto ak8corrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+year+"_"+campaign+"/fatJet_jerc.json");
			auto ak4corrL1 = ak4corrset->at(prompt + jercrun + jecver + "_DATA_L1FastJet" + ak4pf);
			auto ak4corr = ak4corrset->compound().at(prompt + jercrun + jecver + "_DATA_L1L2L3Res" + ak4pf);
			auto ak8corr = ak8corrset->compound().at(prompt + jercrun + jecver + "_DATA_L1L2L3Res" + ak8pf);
	""")
	else:
		ROOT.gInterpreter.Declare("""
			auto ak4corrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+year+"_"+campaign+"/jet_jerc.json");
			auto ak8corrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+year+"_"+campaign+"/fatJet_jerc.json");
			auto ak4corrL1 = ak4corrset->at(prompt + jecver + "_MC_L1FastJet" + ak4pf);
			auto ak4corrUnc = ak4corrset->at(prompt + jecver + "_MC_Total" + ak4pf);
			auto ak4corr = ak4corrset->compound().at(prompt + jecver + "_MC_L1L2L3Res" + ak4pf);
			auto ak4ptres = ak4corrset->at(ak4pt_name);
			auto ak4jer = ak4corrset->at(ak4jer_name);
			auto ak8corrUnc = ak8corrset->at(prompt + jecver + "_MC_Total" + ak8pf);
			auto ak8corr = ak8corrset->compound().at(prompt + jecver + "_MC_L1L2L3Res" + ak8pf);
	""")
	print ("point h - if not isMC/else")

#from muonhltcorr => std::cout << "\t loaded muon trig" << std::endl; // REDO ME (Do we need to change something?)

# ------------------ MET Cuts ------------------
	metCuts = CutGroup('METCuts')
	metCuts.Add('MET Filters', 'Flag_EcalDeadCellTriggerPrimitiveFilter == 1 && Flag_goodVertices == 1 && Flag_HBHENoiseFilter == 1 && Flag_HBHENoiseIsoFilter == 1 && Flag_eeBadScFilter == 1 && Flag_globalSuperTightHalo2016Filter == 1 && Flag_BadPFMuonFilter == 1 && Flag_ecalBadCalibFilter == 1')
	metCuts.Add('Pass MET > 50', 'MET_pt > 50')
	print ("point i")

  # ------------------ Golden JSON (Data) || GEN Info (MC) ------------------
	gjsonVars = VarGroup('GoldenJsonVars')
	gjsonCuts = CutGroup('GoldenJsonCuts')

	gjsonCuts.Add('Event has jets','nJet > 0 && nFatJet > 0') # need jets 

	if not isMC: # apply golden json to data
		gjsonVars.Add("passesJSON", "goldenjson(myLumiMask, run, luminosityBlock)")
		gjsonCuts.Add("Data passes Golden JSON", "passesJSON == 1") 
	else:
		gjsonVars.Add("PileupWeights", "pufunc(corrPU, Pileup_nTrueInt)")

	print ("point j")
  # ------------------ LEPTON Definitions ------------------
	lVars = VarGroup('LeptonVars')

	#if year == "2018": elHEMcut = " && (Electron_eta > -1.479 || (Electron_phi < -1.57 || Electron_phi > -0.87))"
	#ROOT.gInterpreter.Declare('string elHEMcut = "'+elHEMcut+'"; ')
	lVars.Add("Electron_cutBasedIdNoIso_tight", "Electron_cutBasedIdNoIso_tight(nElectron, Electron_vidNestedWPBitmap)")
	lVars.Add("TPassMu", "abs(Muon_eta)<2.4 && Muon_mediumId==1 && Muon_miniIsoId>=3 && abs(Muon_dz) < 0.5 && Muon_dxy < 0.2")
	#lVars.Add("TPassEl", "(abs(Electron_eta)<1.442 || (abs(Electron_eta)>1.566 && abs(Electron_eta)<2.5)) && Electron_cutBasedIdNoIso_tight==1 && Electron_miniPFRelIso_all<0.1"+ elHEMcut)
	lVars.Add("TPassEl", "(abs(Electron_eta)<1.442 || (abs(Electron_eta)>1.566 && abs(Electron_eta)<2.5)) && Electron_cutBasedIdNoIso_tight==1 && Electron_miniPFRelIso_all<0.1")
	lVars.Add("VetoMu", "TPassMu && (Muon_pt>25)")
	lVars.Add("VetoEl", "TPassEl && (Electron_pt>25)")
	lVars.Add("SignalIsoMu", "TPassMu && (Muon_pt>=55)")
	lVars.Add("SignalIsoEl", "TPassEl && (Electron_pt>=55)")
	lVars.Add("nVetoLep", "(int) (Sum(VetoMu)+Sum(VetoEl))")
	lVars.Add("SMuon_pt", "Muon_pt[SignalIsoMu == true]")
	lVars.Add("SMuon_eta", "Muon_eta[SignalIsoMu == true]")
	lVars.Add("SMuon_phi", "Muon_phi[SignalIsoMu == true]")
	lVars.Add("SMuon_mass", "Muon_mass[SignalIsoMu == true]")
	lVars.Add("SElectron_pt", "Electron_pt[SignalIsoEl == true]")
	lVars.Add("SElectron_eta", "Electron_eta[SignalIsoEl == true]")
	lVars.Add("SElectron_phi", "Electron_phi[SignalIsoEl == true]")
	lVars.Add("SElectron_mass", "Electron_mass[SignalIsoEl == true]")
	lVars.Add("Muon_P4", "fVectorConstructor(Muon_pt,Muon_eta,Muon_phi,Muon_mass)")
	lVars.Add("SMuon_P4", "fVectorConstructor(SMuon_pt,SMuon_eta,SMuon_phi,SMuon_mass)")
	lVars.Add("SElectron_P4", "fVectorConstructor(SElectron_pt,SElectron_eta,SElectron_phi,SElectron_mass)")
	lVars.Add("SMuon_jetIdx", "Muon_jetIdx[SignalIsoMu == true]")
	lVars.Add("SElectron_jetIdx", "Electron_jetIdx[SignalIsoEl]")
	lVars.Add("nSignalIsoMu", "(int) Sum(SignalIsoMu)")
	lVars.Add("nSignalIsoEl", "(int) Sum(SignalIsoEl)")
	lVars.Add("VetoIsoMu", "(VetoMu == true && Muon_pt < 55)")
	lVars.Add("VetoIsoEl", "(VetoEl == true && Electron_pt < 55)")
	lVars.Add("nVetoIsoLep", "(int) (Sum(VetoIsoMu)+Sum(VetoIsoEl))")
	print ("point k")
  # ------------------ LEPTON SELECTION ------------------
  
  # ||||||||||||||||||||| TODO ||||||||||||||||||||||||
  ### WE need to find out which triggers exist in run 3
  # ___________________________________________________

	'''tkmutrig = "HLT_Mu15_IsoVVVL_PFHT450 || HLT_Mu50  || HLT_CascadeMu100 || HLT_HighPtTkMu100"
	eltrig = "HLT_Ele15_IsoVVVL_PFHT450 || HLT_Photon200 || HLT_Ele115_CaloIdVT_GsfTrkIdT || HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165"
	'''

	tkmutrig = "HLT_Mu15_IsoVVVL_PFHT450 || HLT_Mu50  || HLT_CascadeMu100 || HLT_HighPtTkMu100"
	eltrig = "HLT_Ele15_IsoVVVL_PFHT450 || HLT_Photon200 || HLT_Ele115_CaloIdVT_GsfTrkIdT || HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165"

	ROOT.gInterpreter.Declare('string tkmutrig = "'+tkmutrig+'"; string eltrig = "'+eltrig+'"; ')

	print ("point l")

	lVars.Add("isMu", "(nMuon>0) && (HLT_Mu50+tkmutrig) && (nSignalIsoMu==1) && (nVetoIsoLep==0) && (nElectron == 0 || nSignalIsoEl == 0)")
	lVars.Add("isEl", "(nElectron>0) && ("+eltrig+") && (nSignalIsoEl==1) && (nVetoIsoLep==0) && (nMuon == 0 || nSignalIsoMu == 0)")
	#lVars.Add("isMu", "(nMuon>0) && (HLT_Mu50) && (nSignalIsoMu==1) && (nVetoIsoLep==0) && (nElectron == 0 || nSignalIsoEl == 0)")
	#lVars.Add("isEl", "(nElectron>0) && (nSignalIsoEl==1) && (nVetoIsoLep==0) && (nMuon == 0 || nSignalIsoMu == 0)")

	print ("point m")

	# filter lepton
	lCuts = CutGroup('LeptonCuts')
	lCuts.Add("Event is either muon or electron", "isMu || isEl")
        # assign lepton
	lVars.Add("assignleps", "assign_leps(isMu,isEl,SignalIsoMu,SignalIsoEl,Muon_pt,Muon_eta,Muon_phi,Muon_mass,Muon_miniPFRelIso_all,Electron_pt,Electron_eta,Electron_phi,Electron_mass,Electron_miniPFRelIso_all)")
	lVars.Add("lepton_pt","assignleps[0]")
	lVars.Add("lepton_eta","assignleps[1]")
	lVars.Add("lepton_phi","assignleps[2]")
	lVars.Add("lepton_mass","assignleps[3]")
	lVars.Add("lepton_miniIso","assignleps[4]")

	print ("point n")
  # ------------------ JET Cleaning and JERC ------------------
	jVars = VarGroup('JetCleaningVars')

	jVars.Add("Jet_P4", "fVectorConstructor(Jet_pt,Jet_eta,Jet_phi,Jet_mass)")
	jVars.Add("FatJet_P4", "fVectorConstructor(FatJet_pt,FatJet_eta,FatJet_phi,FatJet_mass)")
	jVars.Add("Jet_EmEF","Jet_neEmEF + Jet_chEmEF")
	jVars.Add("DummyZero","float(0.0)")
          # Clean Jets
	if isMC:          #TODO fix dummy comments
		jVars.Add("GenJet_P4","fVectorConstructor(GenJet_pt,GenJet_eta,GenJet_phi,GenJet_mass)")
		jVars.Add("cleanedJets", "cleanJetsMC(debug,campaign,jesvar,ak4corr,ak4corrL1,ak4corrUnc,ak4ptres,ak4jer,ak8corr,ak8corrUnc,Jet_P4,Jet_rawFactor,Jet_muonSubtrFactor,Jet_area,Jet_EmEF,Jet_jetId,GenJet_P4,Jet_genJetIdx,SMuon_P4,SMuon_jetIdx,SElectron_P4,SElectron_jetIdx,Rho_fixedGridRhoFastjetAll,DummyZero,DummyZero)") # muon and EM factors unused in this call
		jVars.Add("cleanMets", "cleanJetsMC(debug,campaign,jesvar,ak4corr,ak4corrL1,ak4corrUnc,ak4ptres,ak4jer,ak8corr,ak8corrUnc,Jet_P4,Jet_rawFactor,Jet_muonSubtrFactor,Jet_area,Jet_EmEF,Jet_jetId,GenJet_P4,Jet_genJetIdx,SMuon_P4,SMuon_jetIdx,SElectron_P4,SElectron_jetIdx,Rho_fixedGridRhoFastjetAll,RawMET_pt,RawMET_phi)") # lepton args are unused in this call
		jVars.Add("GenJetAK8_P4", "fVectorConstructor(GenJetAK8_pt,GenJetAK8_eta,GenJetAK8_phi,GenJetAK8_mass)")
		jVars.Add("cleanFatJets", "cleanJetsMC(debug,campaign,jesvar,ak4corr,ak4corrL1,ak4corrUnc,ak4ptres,ak4jer,ak8corr,ak8corrUnc,FatJet_P4,FatJet_rawFactor,FatJet_rawFactor,FatJet_area,FatJet_area,FatJet_jetId,GenJetAK8_P4,FatJet_genJetAK8Idx,SMuon_P4,SMuon_jetIdx,SElectron_P4,SElectron_jetIdx,Rho_fixedGridRhoFastjetAll,DummyZero,DummyZero)") # args 12 and 14 are dummies
	else:
      # Replace all the GenJet arguments with fakes here for data. 
		jVars.Add("cleanedJets", "cleanJetsData(debug,campaign,ak4corr,ak4corrL1,ak8corr,Jet_P4,Jet_rawFactor,Jet_muonSubtrFactor,Jet_area,Jet_EmEF,Jet_jetId,Jet_P4,Jet_jetId,SMuon_P4,SMuon_jetIdx,SElectron_P4,SElectron_jetIdx,Rho_fixedGridRhoFastjetAll,DummyZero,DummyZero)") # muon and EM factors unused in this call, args 16-17 are dummies
		jVars.Add("cleanMets", "cleanJetsData(debug,campaign,ak4corr,ak4corrL1,ak8corr,Jet_P4,Jet_rawFactor,Jet_muonSubtrFactor,Jet_area,Jet_EmEF,Jet_jetId,Jet_P4,Jet_jetId,Muon_P4,Muon_jetIdx,SElectron_P4,SElectron_jetIdx,Rho_fixedGridRhoFastjetAll,RawMET_pt,RawMET_phi)") # lepton args unused in this call, args 16-17 are dummies
		jVars.Add("cleanFatJets", "cleanJetsData(debug,campaign,ak4corr,ak4corrL1,ak8corr,FatJet_P4,FatJet_rawFactor,FatJet_rawFactor,FatJet_area,FatJet_area,FatJet_jetId,FatJet_P4,FatJet_jetId,SMuon_P4,SMuon_jetIdx,SElectron_P4,SElectron_jetIdx,Rho_fixedGridRhoFastjetAll,DummyZero,DummyZero)") # args 12, 14, 16, 17 are dummies 
	print ("point o")

	#Jet Assign
	jVars.Add("cleanJet_pt", "cleanedJets[0]")
	jVars.Add("cleanJet_eta", "cleanedJets[1]")
	jVars.Add("cleanJet_phi", "cleanedJets[2]")
	jVars.Add("cleanJet_mass", "cleanedJets[3]")
	jVars.Add("cleanFatJet_pt", "cleanFatJets[0]")
	jVars.Add("cleanFatJet_eta", "cleanFatJets[1]")
	jVars.Add("cleanFatJet_phi", "cleanFatJets[2]")
	jVars.Add("cleanFatJet_mass", "cleanFatJets[3]")

	print("point p")
# ------------------ MET Selection ------------------
	metVars = VarGroup('METVars')
#remove "noxy" from names underneath (bc noxy corrections don't exist)
	metVars.Add("corrMET_pt","cleanMets[4][0]")
	metVars.Add("corrMET_phi","cleanMets[4][1]")
	#comment out next three below
	#metVars.Add("metxyoutput", "metfunc(metptcorr, metphicorr, corrMETnoxy_pt, corrMETnoxy_phi, PV_npvs, run)")

	#metVars.Add("corrMET_pt","metxyoutput[0]")
	#metVars.Add("corrMET_phi","metxyoutput[1]")

	metCuts.Add("Pass corr MET > 60", "corrMET_pt > 60")
	metCuts.Add("Electron Triangle Cut", "isMu || corrMET_pt>((130/1.5)*DeltaPhi(lepton_phi, corrMET_phi)-130)")

  # ------------------ HT Calculation and N Jets cuts ------------------
	jVars.Add("DR_lepJets","DeltaR_VecAndFloat(cleanJet_eta,cleanJet_phi,lepton_eta,lepton_phi)")
	jVars.Add("ptrel_lepJets","ptRel(cleanJet_pt,cleanJet_eta,cleanJet_phi,cleanJet_mass,lepton_pt,lepton_eta,lepton_phi,lepton_mass)") 
	jVars.Add("goodcleanJets", "cleanJet_pt > 30 && abs(cleanJet_eta) < 2.4 && Jet_jetId > 1 && (DR_lepJets > 0.4 || ptrel_lepJets > 20)")
	jVars.Add("gcJet_HT","Sum(cleanJet_pt[goodcleanJets == true])")
	jVars.Add("DR_lepFatJets","DeltaR_VecAndFloat(FatJet_eta,FatJet_phi,lepton_eta,lepton_phi)")
	jVars.Add("ptrel_lepFatJets","ptRel(FatJet_pt,FatJet_eta,FatJet_phi,FatJet_mass,lepton_pt,lepton_eta,lepton_phi,lepton_mass)")   #TODO not in BtoTW
	jVars.Add("goodcleanFatJets", "FatJet_pt > 200 && abs(FatJet_eta) < 2.4 && FatJet_jetId > 1 && (DR_lepFatJets > 0.8 || ptrel_lepFatJets > 20)")
  #TODO which one do we want?  jVars.Add("goodcleanFatJets", "cleanFatJet_pt > 200 && abs(cleanFatJet_eta) < 2.5 && FatJet_jetId > 1 && (DR_lepFatJets > 0.8)")
	jVars.Add("NFatJets", "(int) Sum(goodcleanFatJets)")

	jCuts = CutGroup('JetCuts')

	jCuts.Add('Pass HT > 510', 'gcJet_HT > 510') # change to? > 250   
	jCuts.Add('3 AK8s Pass', 'NFatJets > 2')  #TODO change to? > 0      # need to ensure three jets exist


  # ------------------ Jet pt ordering, counting, lepton association ------------------
	jVars.Add("gcJet_pt_unsort", "cleanJet_pt[goodcleanJets == true]")
	jVars.Add("gcJet_ptargsort","ROOT::VecOps::Reverse(ROOT::VecOps::Argsort(gcJet_pt_unsort))")
	jVars.Add("gcJet_pt","reorder(gcJet_pt_unsort,gcJet_ptargsort)")
	jVars.Add("gcJet_eta", "reorder(cleanJet_eta[goodcleanJets == true],gcJet_ptargsort)")
	jVars.Add("gcJet_phi", "reorder(cleanJet_phi[goodcleanJets == true],gcJet_ptargsort)")
	jVars.Add("gcJet_mass", "reorder(cleanJet_mass[goodcleanJets == true],gcJet_ptargsort)")
	jVars.Add("gcJet_vetomap", "jetvetofunc(jetvetocorr, gcJet_eta, gcJet_phi)")
          #fatjet vars
	jVars.Add("gcFatJet_pt_unsort", "FatJet_pt[goodcleanFatJets == true]")
	jVars.Add("gcFatJet_ptargsort","ROOT::VecOps::Reverse(ROOT::VecOps::Argsort(gcFatJet_pt_unsort))")
	jVars.Add("gcFatJet_pt","reorder(gcFatJet_pt_unsort,gcFatJet_ptargsort)")
	jVars.Add("gcFatJet_eta", "reorder(FatJet_eta[goodcleanFatJets == true],gcFatJet_ptargsort)")
	jVars.Add("gcFatJet_phi", "reorder(FatJet_phi[goodcleanFatJets == true],gcFatJet_ptargsort)")
	jVars.Add("gcFatJet_mass", "reorder(FatJet_mass[goodcleanFatJets == true],gcFatJet_ptargsort)")
	jVars.Add("gcFatJet_sdmass", "reorder(FatJet_msoftdrop[goodcleanFatJets == true],gcFatJet_ptargsort)")
	jVars.Add("gcFatJet_vetomap", "jetvetofunc(jetvetocorr, gcFatJet_eta, gcFatJet_phi)")
  	#condition to only return isolated jets (not inside a fatjet), needs gcJet_* and gcFatJet_*
	jVars.Add("Isolated_AK4","standalone_Jet(gcJet_eta, gcJet_phi, gcFatJet_eta, gcFatJet_phi)")

  # ------------------ Add scale factors and MC jet-based calcs ------------------
  #TODO could be a fatJetVar group
	if isMC:
    #jVars.Add("genttbarMass", Form("genttbarMassCalc(\"%s\", nGenPart, GenPart_pdgId, GenPart_mass, GenPart_pt, GenPart_phi, GenPart_eta, GenPart_genPartIdxMother, GenPart_status)",sample.c_str()))
		jVars.Add("genttbarMass", "genttbarMassCalc(\""+sample+"\", nGenPart, GenPart_pdgId, GenPart_mass, GenPart_pt, GenPart_phi, GenPart_eta, GenPart_genPartIdxMother, GenPart_status)")
		jVars.Add("leptonRecoSF", "recofunc(electroncorr, muoncorr, campaign, lepton_pt, lepton_eta, isEl)")
		jVars.Add("leptonIDSF", "idfunc(muonidcorr,elid_pts,elid_etas,elecidsfs,elecidsfuncs,campaign, lepton_pt, lepton_eta, isEl)") #at(0) 
		jVars.Add("leptonIsoSF", "isofunc(muiso_pts,muiso_etas,muonisosfs,muonisosfunc,elid_pts,elid_etas,elecisosfs,elecisosfunc, lepton_pt, lepton_eta, isEl)")
		jVars.Add("leptonHLTSF", "hltfunc(elhlt_pts,elhlt_etas,elechltsfs,elechltuncs,campaign, lepton_pt, lepton_eta, isEl)")

# ------------------ Results ------------------
	rframeVars = VarGroup('restFrameVars')
	rframeVars.Add('VLQ_mass', 'rfc.compute_mass(rdfslot_, lepton_pt, lepton_eta, lepton_phi, lepton_mass, gcFatJet_pt, gcFatJet_eta, gcFatJet_phi, gcFatJet_mass, MET_pt, MET_phi)')
	rframeVars.Add('VLQ_mass_T', 'VLQ_mass[0]')
	rframeVars.Add('VLQ_mass_Tbar', 'VLQ_mass[1]')
	rframeVars.Add('VLQ_mass_T_r', 'VLQ_mass[2]')
	rframeVars.Add('VLQ_mass_Tbar_r', 'VLQ_mass[3]')
	rframeVars.Add('VLQ_mass_ratio', 'VLQ_mass_T/VLQ_mass_Tbar')
	rframeVars.Add('VLQ_mass_avg', '(VLQ_mass_T+VLQ_mass_Tbar)*0.5')

# ------------------ Apply Var and Cut Groups------------------ 

#	nodeToPlot = a.Apply([gjsonVars, gjsonCuts]) 
	nodeToPlot = a.Apply([gjsonVars, gjsonCuts, lVars, lCuts]) 

  # Solution to cleanJets() problem:
  #       The analyzer .Apply() calls the analyzer .Define().  This .Define() calls self._collectionOrg.CollectionDefCheck(var, newNode).
  #  This method executes this line: if re.search(r"\b" + re.escape(c+'s') + r"\b", action_str) and (c+'s' not in self._builtCollections):
  #                                       print ('MAKING %ss for %s'%(c,action_str))
  #  Apparently somethings get discarded from this _collectionOrg?
  #  Instead force the .Apply() from the ActiveNode because the node .Apply() is better.

	newNode = a.ActiveNode.Apply(jVars)
	a.SetActiveNode(newNode)

	a.Apply([jCuts, metVars, metCuts, rframeVars])

	allColumns = a.GetColumnNames()
	columns = [] #allColumns

	i = 0
	for col in allColumns:
		if col == "run": break #TODO delete? or lets just skip all the original branches?

		if ("P4" in col) or ("cleanedJets" in col) or ("cleanFatJets" in col) or ("cleanMets" in col) or ("Dummy" in col): continue 
		if ("LHE" in col) and ("Weight" not in col) and (col != "LHE_HT") and (col != "LHE_Vpt") and (col != "gcHTCorr_WjetLHE"): continue
		if col.startswith("Muon") and ("_tightId" not in col) and ("_isPF" not in col) and ("tunep" not in col) and ("genPartFlav" not in col): continue
		if col.startswith("Electron") and ("genPartFlav" not in col): continue
		if col.startswith("Jet") and ("rawFactor" not in col): continue
		if col.startswith("FatJet") and ("rawFactor" not in col): continue
		if col.startswith("PPS") or col.startswith("Proton") or col.startswith("L1_"): continue
		if col.startswith("Gen") or col.startswith("Soft") or col.startswith("fixed"): continue
		if col.startswith("Sub") or col.startswith("RawPuppi") or col.startswith("Calo") or col.startswith("Chs"): continue
		if col.startswith("Corr") or col.startswith("Fsr") or col.startswith("Iso") or col.startswith("Tau"): continue
		if col.startswith("SV") or col.startswith("Puppi") or col.startswith("Photon") or col.startswith("Low"): continue
		if col.startswith("HLT") or col.startswith("HT") or col.startswith("boosted") or col.startswith("Deep"): continue
		if col.startswith("Flag") or col == "Bprime_gen_info" or col == "t_gen_info" or col == "W_gen_info" or col == "metxyoutput": continue
		if col == "assignleps" or col == "pnetoutput" or col == "t_output" or col == "Bprime_output" or col.startswith("Other"): continue
		if col.startswith("PS") or col.startswith("PV") or col.startswith("Tk") or col.startswith("Trig"): continue
		if col.startswith("nCorr") or col.startswith("nFsr"): continue
		if col.startswith("nGen") or col.startswith("nIso") or col.startswith("nLow"): continue
		if col.startswith("nOther") or col.startswith("nPS") or col.startswith("nPhoton"): continue
		if col.startswith("nSV") or col.startswith("nSub") or col.startswith("nTau") or col.startswith("nTrig"): continue
		if col.startswith("nboosted"): continue
    #TODO need to figure out how to exclude the things related to nSub and Sub.
		columns.append(col)
		i = i + 1
    #if i > 49: continue

  #TODO think do we really want to recreate this everytime?  or just create?

  #dataera = (C,D,E,F,G or _ext1-3) ; procver = (v1-v4 for data, empty string for isMC)
	finalFile = "RDF_" + sample + dataera + procver + "_" + year + "_" + str(testNum1) + ".root"

  #TODO ROOT::RDF::RSnapshotOptions opts;
  #if(jesvar != "Nominal") opts.fMode = "UPDATE";

  #TODO do we want the REPORT on the filter statistics?
	a.Snapshot(columns, finalFile, "Events", lazy=False, openOption='RECREATE', saveRunChain=False)
	print(f"Number of Columns in Snapshot: {i}")

	print(f"Saved file = {finalFile}")

	#myHist1 = a.GetActiveNode().DataFrame.Histo1D(('m_T_lab', 'Mass of T lab', 25, 500, 2000), 'VLQ_mass_T')
	#myHist2 = a.GetActiveNode().DataFrame.Histo1D(('m_Tbar_lab', 'Mass of Tbar lab', 25, 500, 2000), 'VLQ_mass_Tbar')
	#myHist1a = a.GetActiveNode().DataFrame.Histo1D(('m_T', 'Mass of T', 25, 500, 2000), 'VLQ_mass_T_r')
	#myHist2a = a.GetActiveNode().DataFrame.Histo1D(('m_Tbar', 'Mass of Tbar', 25, 500, 2000), 'VLQ_mass_Tbar_r')
	#myHist3 = a.GetActiveNode().DataFrame.Histo1D(('m_T/m_Tbar', 'Mass ratio of the two particles', 25, 0, 2), 'VLQ_mass_ratio')
	#myHist4 = a.GetActiveNode().DataFrame.Histo1D(('m_avg', 'Mass average of the two', 25, 500, 2000), 'VLQ_mass_avg')

	#out = ROOT.TFile.Open('test'+campaign+'_Tprime_out.root','RECREATE') #'UPDATE')
	#myHist1.Write()
	#myHist2.Write()
	#myHist1a.Write()
	#myHist2a.Write()
	#myHist3.Write()
	#myHist4.Write()

	#out.Close()

	print("Cut statistics:")
	rep = a.DataFrame.Report()
	rep.Print()
	print("Got past the report")

	print("--------- Analysis End ---------")

	a.Close()

if not isMC:
	analyze("Nominal")
else:
	shifts = ["Nominal","JECup","JECdn","JERup","JERdn"]
	for shift in shifts:
		analyze(shift)

os.remove('trimmed_input.txt')
