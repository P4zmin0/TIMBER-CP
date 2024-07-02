from TIMBER.Analyzer import *
from TIMBER.Tools.Common import *

import ROOT
from ROOT import TFile
import sys, os
import gc

gc.disable()

from TIMBER.Tools.RestFramesHandler import load_restframes

# From https://gist.github.com/pieterdavid/a560e65658386d70a1720cb5afe4d3e9#file-df-py  example
import correctionlib
correctionlib.register_pyroot_binding()

sys.path.append('../../')
sys.path.append('../../../')

num_threads = 1
#file_name = 'root://cmsxrootd.fnal.gov//store/mc/RunIISummer20UL18NanoAODv9/TprimeTprime_M-1500_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/40000/447AD74F-034B-FA42-AD05-CD476A98C43D.root'
file_name = 'ourtestfile.root'

# Import the C++
CompileCpp('TIMBER/Framework/include/common.h') # Compile (via gInterpreter) commonly used c++ code
CompileCpp('TIMBER/Framework/Tprime1lep/cleanjet.cc') # Compile Our vlq c++ code
CompileCpp('TIMBER/Framework/Tprime1lep/utilities.cc') # Compile Our vlq c++ code
CompileCpp('TIMBER/Framework/Tprime1lep/lumiMask.cc')
CompileCpp('TIMBER/Framework/Tprime1lep/selfDerived_corrs.cc')
CompileCpp('TIMBER/Framework/Tprime1lep/corrlib_funcs.cc') 
CompileCpp('TIMBER/Framework/Tprime1lep/generatorInfo.cc')
ROOT.gInterpreter.ProcessLine('#include "TString.h"')

handler_name = 'Tprime_handler.cc'
class_name = 'Tprime_RestFrames_Container'

# Enable using 4 threads
ROOT.ROOT.EnableImplicitMT(num_threads)

# load rest frames handler
load_restframes(num_threads, handler_name, class_name, 'rfc')

# Create analyzer instance
a = analyzer(file_name)

print('==========================INITIALIZED ANALYZER========================')

# ------------------ Command Line Arguments ------------------
year = sys.argv[1]

# ------------------ Important Variables ------------------

#TODO translate the code from BtoTW analyzer_RDF.h for the 4 arguments.  filelist.txt num1 num2

#isMC? isVV? isSig? etc.
sample = "TprimeTprime_M-1500_TuneCP5_13TeV-madgraph-pythia8"
isMC = True #False
'''if "/mc/" in file_name:
  isMC = True
else: 
  isMC = False'''
#   isMC = !(sampleName.Contains("Single") || sampleName.Contains("Data18") || sampleName.Contains("EGamma"));

isData = False
#   if(inputFile.find("Single") != std::string::npos || inputFile.find("EGamma") != std::string::npos) isData = true;

jesvar = "Nominal"
if not isData:
  jesvar; # will have it run through each of the options
  #"Nominal","JECup","JECdn","JERup","JERdn"

debug = False

#TODO test this isMC
ROOT.gInterpreter.Declare("""
string year = "' + year + '"; 
string sample = "' + sample + '";

bool isMC = """+str(isMC).lower()+"""; 

bool debug = false; //\""""+str(debug)+"""\"; 
string jesvar = "' + jesvar + '"; 
string jecera = "D";
""")

# ------------------ Golden JSON Data ------------------
# change the jsonfile path to somewhere they have it in TIMBER
jsonfile = "../TIMBER/data/LumiJSON/"
if (year == "2016" or year == "2016APV"): jsonfile = jsonfile + "Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"
elif (year == "2017"): jsonfile = jsonfile + "Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt"
elif (year == "2018"): jsonfile = jsonfile + "Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"
else: print(f'ERROR: Can\'t parse the year to assign a golden json file. Expected 2016, 2016APV, 2017, or 2018. Got: {year}\n')

ROOT.gInterpreter.Declare("""
const auto myLumiMask = lumiMask::fromJSON(\"""" + jsonfile + """\");
//  std::cout << "Testing the JSON! Known good run/lumi returns: " << myLumiMask.accept(315257, 10) << ", and known bad run returns: " << myLumiMask.accept(315257, 90) << std::endl;
""")

# ------------------ Self-derived corrections ------------------

#TODO more things here

    # Lepton scale factors not in correctionLib
ROOT.gInterpreter.ProcessLine('initialize(year);')

#can do things like this inside:   include <iostream>
#using namespace std; 
#std::cout << elid_pts.size() << elid_pts.at(2); //TODO remove
#std::cout << elecidsfs.size() << elecidsfs.at(0).size() << elecidsfs.at(0).at(0) << endl;
#""")

# ------------------ correctionsLib corrections ------------------
mutrig = "TkMu50";
if (year == "2016APV"): deepjetL = "0.0508"; yrstr = "2016preVFP"; yr = "16"; jecyr = "UL16APV"; jeryr = "Summer20UL16APV_JRV3"; jecver = "V7"
elif (year == "2016"): deepjetL = "0.0480"; yrstr = "2016postVFP"; yr = "16"; jecyr = "UL16"; jeryr = "Summer20UL16_JRV3"; jecver = "V7"
elif (year == "2017"): mutrig = "OldMu100_or_TkMu100"; deepjetL = "0.0532"; yrstr = "2017"; yr = "17"; jecyr = "UL17"; jeryr = "Summer19UL17_JRV2"; jecver = "V5"
elif (year == "2018"): mutrig = "OldMu100_or_TkMu100"; deepjetL = "0.0490"; yrstr = "2018"; yr = "18"; jecyr = "UL18"; jeryr = "Summer19UL18_JRV2"; jecver = "V5"
else: print(f'ERROR: Can\'t parse the year to assign correctionLib json files. Expected 2016, 2016APV, 2017, or 2018. Got: {year}\n')

ROOT.gInterpreter.Declare("""
string yrstr = \""""+yrstr+"""\"; string yr = \""""+yr+"""\"; string jecyr = \""""+jecyr+"""\"; string jeryr = \""""+jeryr+"""\"; string jecver = \""""+jecver+"""\"; string mutrig = \""""+mutrig+"""\";
float deepjetL = """+deepjetL+"""; 
""")


ROOT.gInterpreter.Declare("""
auto csetPU = correction::CorrectionSet::from_file("jsonpog-integration/POG/LUM/"+yrstr+"_UL/puWeights.json");
auto electroncorrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/EGM/"+yrstr+"_UL/electron.json");
auto muoncorrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/MUO/"+yrstr+"_UL/muon_Z.json");
auto jetvetocorrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+yrstr+"_UL/jetvetomaps.json");

auto corrPU = csetPU->at("Collisions"+yr+"_UltraLegacy_goldenJSON");
auto electroncorr = electroncorrset->at("UL-Electron-ID-SF"); 
auto muoncorr = muoncorrset->at("NUM_TrackerMuons_DEN_genTracks");
auto muonidcorr = muoncorrset->at("NUM_MediumID_DEN_TrackerMuons");
auto muonhltcorr = muoncorrset->at("NUM_Mu50_or_"+mutrig+"_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose"); 
auto jetvetocorr = jetvetocorrset->at("Summer19UL"+yr+"_V1");
""") 
if not isMC:
  ROOT.gInterpreter.Declare("""
    auto ak4corrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+yrstr+"_UL/jet_jerc.json"); 
    auto ak8corrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+yrstr+"_UL/fatJet_jerc.json"); 
    auto metcorrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+yrstr+"_UL/met.json");
    
    auto metptcorr = metcorrset->at("pt_metphicorr_pfmet_data");
    auto metphicorr = metcorrset->at("phi_metphicorr_pfmet_data"); 

    auto ak4corrL1 = ak4corrset->at("Summer19"+jecyr+"_Run"+jecera+"_"+jecver+"_DATA_L1FastJet_AK4PFchs"); 
    auto ak4corr = ak4corrset->compound().at("Summer19"+jecyr+"_Run"+jecera+"_"+jecver+"_DATA_L1L2L3Res_AK4PFchs");
    auto ak8corr = ak8corrset->compound().at("Summer19"+jecyr+"_Run"+jecera+"_"+jecver+"_DATA_L1L2L3Res_AK8PFPuppi"); 
  """)
else:
  ROOT.gInterpreter.Declare("""
    auto ak4corrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+yrstr+"_UL/jet_jerc.json"); 
    auto ak8corrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+yrstr+"_UL/fatJet_jerc.json"); 
    auto metcorrset = correction::CorrectionSet::from_file("jsonpog-integration/POG/JME/"+yrstr+"_UL/met.json");
    
    auto metptcorr = metcorrset->at("pt_metphicorr_pfmet_mc");
    auto metphicorr = metcorrset->at("phi_metphicorr_pfmet_mc");
    
    auto ak4corrL1 = ak4corrset->at("Summer19"+jecyr+"_"+jecver+"_MC_L1FastJet_AK4PFchs"); 
    auto ak4corrUnc = ak4corrset->at("Summer19"+jecyr+"_"+jecver+"_MC_Total_AK4PFchs"); 
    auto ak4corr = ak4corrset->compound().at("Summer19"+jecyr+"_"+jecver+"_MC_L1L2L3Res_AK4PFchs");

    auto ak4ptres = ak4corrset->at(jeryr+"_MC_PtResolution_AK4PFchs"); 
    auto ak4jer = ak4corrset->at(jeryr+"_MC_ScaleFactor_AK4PFchs"); 
    auto ak8corrUnc = ak8corrset->at("Summer19"+jecyr+"_"+jecver+"_MC_Total_AK8PFPuppi");
    auto ak8corr = ak8corrset->compound().at("Summer19"+jecyr+"_"+jecver+"_MC_L1L2L3Res_AK8PFPuppi");
  """)

#from muonhltcorr => std::cout << "\t loaded muon trig" << std::endl; // REDO ME (Do we need to change something?)

# ------------------ MET Cuts ------------------
metCuts = CutGroup('METCuts')
metCuts.Add('MET Filters', 'Flag_EcalDeadCellTriggerPrimitiveFilter == 1 && Flag_goodVertices == 1 && Flag_HBHENoiseFilter == 1 && Flag_HBHENoiseIsoFilter == 1 && Flag_eeBadScFilter == 1 && Flag_globalSuperTightHalo2016Filter == 1 && Flag_BadPFMuonFilter == 1 && Flag_ecalBadCalibFilter == 1')
metCuts.Add('Pass MET > 50', 'MET_pt > 50')
metCuts.Add('Event has jets',        'nJet > 0 && nFatJet > 0') # need jets 

# ------------------ Golden JSON (Data) || GEN Info (MC) ------------------
gjsonVars = VarGroup('GoldenJsonVars')
gjsonCuts = CutGroup('GoldenJsonCuts')
if not isMC: # apply golden json to data
  gjsonVars.Add("passesJSON", "goldenjson(myLumiMask, run, luminosityBlock)")
  gjsonCuts.Add("Data passes Golden JSON", "passesJSON == 1") 
else:
  gjsonVars.Add("PileupWeights", "pufunc(corrPU, Pileup_nTrueInt)")

# ------------------ LEPTON Definitions ------------------
lVars = VarGroup('LeptonVars')

if year == "2018": elHEMcut = " && (Electron_eta > -1.479 || (Electron_phi < -1.57 || Electron_phi > -0.87))"
ROOT.gInterpreter.Declare('string elHEMcut = "'+elHEMcut+'"; ')

lVars.Add("Electron_cutBasedIdNoIso_tight", "Electron_cutBasedIdNoIso_tight(nElectron, Electron_vidNestedWPBitmap)")
lVars.Add("TPassMu", "abs(Muon_eta)<2.4 && Muon_mediumId==1 && Muon_miniIsoId>=3 && abs(Muon_dz) < 0.5 && Muon_dxy < 0.2")
#lVars.Add("TPassEl", "Form(\"(abs(Electron_eta)<1.442 || (abs(Electron_eta)>1.566 && abs(Electron_eta)<2.5)) && Electron_cutBasedIdNoIso_tight==1 && Electron_miniPFRelIso_all<0.1%s\",elHEMcut.c_str())")
lVars.Add("TPassEl", "(abs(Electron_eta)<1.442 || (abs(Electron_eta)>1.566 && abs(Electron_eta)<2.5)) && Electron_cutBasedIdNoIso_tight==1 && Electron_miniPFRelIso_all<0.1"+ elHEMcut)
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

# ------------------ LEPTON SELECTION ------------------

# ||||||||||||||||||||| TODO ||||||||||||||||||||||||
### WE need to find out which triggers exist in run 3
# ___________________________________________________

tkmutrig = " || HLT_OldMu100 || HLT_TkMu100"
eltrig = "HLT_Ele115_CaloIdVT_GsfTrkIdT || HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165 || HLT_Photon200"
if(year == "2017" and era == "B"): 
  tkmutrig = ""
  eltrig = "HLT_Ele35_WPTight_Gsf || HLT_Photon200"
if(year == "2016" or year == "2016APV"):
  tkmutrig = " || HLT_TkMu50"
  eltrig = "HLT_Ele115_CaloIdVT_GsfTrkIdT || HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165 || HLT_Photon175"
if(year == "2016APV" and (era == "A" or era == "B")):
    tkmutrig = ""
    eltrig = "HLT_Ele115_CaloIdVT_GsfTrkIdT || HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165 || HLT_Photon175"
ROOT.gInterpreter.Declare('string tkmutrig = "'+tkmutrig+'"; string eltrig = "'+eltrig+'"; ')

#lVars.Add("isMu", "Form(\"(nMuon>0) && (HLT_Mu50%s) && (nSignalIsoMu==1) && (nVetoIsoLep==0) && (nElectron == 0 || nSignalIsoEl == 0)\",tkmutrig.c_str())")
#lVars.Add("isEl", "Form(\"(nElectron>0) && (%s) && (nSignalIsoEl==1) && (nVetoIsoLep==0) && (nMuon == 0 || nSignalIsoMu == 0)\",eltrig.c_str())")
lVars.Add("isMu", "(nMuon>0) && (HLT_Mu50"+ tkmutrig +") && (nSignalIsoMu==1) && (nVetoIsoLep==0) && (nElectron == 0 || nSignalIsoEl == 0)")
lVars.Add("isEl", "(nElectron>0) && ("+ eltrig +") && (nSignalIsoEl==1) && (nVetoIsoLep==0) && (nMuon == 0 || nSignalIsoMu == 0)")
        
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


# ------------------ JET Cleaning and JERC ------------------
jVars = VarGroup('JetCleaningVars')

jVars.Add("Jet_P4", "fVectorConstructor(Jet_pt,Jet_eta,Jet_phi,Jet_mass)")
jVars.Add("FatJet_P4", "fVectorConstructor(FatJet_pt,FatJet_eta,FatJet_phi,FatJet_mass)")
jVars.Add("Jet_EmEF","Jet_neEmEF + Jet_chEmEF")
jVars.Add("DummyZero","float(0.0)")
        # Clean Jets
if isMC:          #TODO fix dummy comments
  jVars.Add("GenJet_P4","fVectorConstructor(GenJet_pt,GenJet_eta,GenJet_phi,GenJet_mass)")
  jVars.Add("cleanedJets", "cleanJetsMC(debug,jesvar,ak4corr,ak4corrL1,ak4corrUnc,ak4ptres,ak4jer,ak8corr,ak8corrUnc,Jet_P4,Jet_rawFactor,Jet_muonSubtrFactor,Jet_area,Jet_EmEF,Jet_jetId,GenJet_P4,Jet_genJetIdx,SMuon_P4,SMuon_jetIdx,SElectron_P4,SElectron_jetIdx,fixedGridRhoFastjetAll,DummyZero,DummyZero)") # muon and EM factors unused in this call
  jVars.Add("cleanMets", "cleanJetsMC(debug,jesvar,ak4corr,ak4corrL1,ak4corrUnc,ak4ptres,ak4jer,ak8corr,ak8corrUnc,Jet_P4,Jet_rawFactor,Jet_muonSubtrFactor,Jet_area,Jet_EmEF,Jet_jetId,GenJet_P4,Jet_genJetIdx,SMuon_P4,SMuon_jetIdx,SElectron_P4,SElectron_jetIdx,fixedGridRhoFastjetAll,RawMET_pt,RawMET_phi)") # lepton args are unused in this call
  jVars.Add("GenJetAK8_P4", "fVectorConstructor(GenJetAK8_pt,GenJetAK8_eta,GenJetAK8_phi,GenJetAK8_mass)")
  jVars.Add("cleanFatJets", "cleanJetsMC(debug,jesvar,ak4corr,ak4corrL1,ak4corrUnc,ak4ptres,ak4jer,ak8corr,ak8corrUnc,FatJet_P4,FatJet_rawFactor,FatJet_rawFactor,FatJet_area,FatJet_area,FatJet_jetId,GenJetAK8_P4,FatJet_genJetAK8Idx,SMuon_P4,SMuon_jetIdx,SElectron_P4,SElectron_jetIdx,fixedGridRhoFastjetAll,DummyZero,DummyZero)") # args 12 and 14 are dummies
else:
    # Replace all the GenJet arguments with fakes here for data. 
  jVars.Add("cleanedJets", "cleanJetsData(debug,ak4corr,ak4corrL1,ak8corr,Jet_P4,Jet_rawFactor,Jet_muonSubtrFactor,Jet_area,Jet_EmEF,Jet_jetId,Jet_P4,Jet_jetId,SMuon_P4,SMuon_jetIdx,SElectron_P4,SElectron_jetIdx,fixedGridRhoFastjetAll,DummyZero,DummyZero)") # muon and EM factors unused in this call, args 16-17 are dummies
  jVars.Add("cleanMets", "cleanJetsData(debug,ak4corr,ak4corrL1,ak8corr,Jet_P4,Jet_rawFactor,Jet_muonSubtrFactor,Jet_area,Jet_EmEF,Jet_jetId,Jet_P4,Jet_jetId,Muon_P4,Muon_jetIdx,SElectron_P4,SElectron_jetIdx,fixedGridRhoFastjetAll,RawMET_pt,RawMET_phi)") # lepton args unused in this call, args 16-17 are dummies
  jVars.Add("cleanFatJets", "cleanJetsData(debug,ak4corr,ak4corrL1,ak8corr,FatJet_P4,FatJet_rawFactor,FatJet_rawFactor,FatJet_area,FatJet_area,FatJet_jetId,FatJet_P4,FatJet_jetId,SMuon_P4,SMuon_jetIdx,SElectron_P4,SElectron_jetIdx,fixedGridRhoFastjetAll,DummyZero,DummyZero)") # args 12, 14, 16, 17 are dummies
        # Jet Assign
jVars.Add("cleanJet_pt", "cleanedJets[0]")
jVars.Add("cleanJet_eta", "cleanedJets[1]")
jVars.Add("cleanJet_phi", "cleanedJets[2]")
jVars.Add("cleanJet_mass", "cleanedJets[3]")
jVars.Add("cleanFatJet_pt", "cleanFatJets[0]")
jVars.Add("cleanFatJet_eta", "cleanFatJets[1]")
jVars.Add("cleanFatJet_phi", "cleanFatJets[2]")
jVars.Add("cleanFatJet_mass", "cleanFatJets[3]")


# ------------------ MET Selection ------------------
metVars = VarGroup('METVars')

metVars.Add("corrMETnoxy_pt","cleanMets[4][0]")
metVars.Add("corrMETnoxy_phi","cleanMets[4][1]")

metVars.Add("metxyoutput", "metfunc(metptcorr, metphicorr, corrMETnoxy_pt, corrMETnoxy_phi, PV_npvs, run)")

metVars.Add("corrMET_pt","metxyoutput[0]")
metVars.Add("corrMET_phi","metxyoutput[1]")

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
  jVars.Add("leptonRecoSF", "recofunc(electroncorr, muoncorr, yrstr, lepton_pt, lepton_eta, isEl)")
  jVars.Add("leptonIDSF", "idfunc(muonidcorr,elid_pts,elid_etas,elecidsfs,elecidsfuncs,yrstr, lepton_pt, lepton_eta, isEl)") #at(0) 
  jVars.Add("leptonIsoSF", "isofunc(muiso_pts,muiso_etas,muonisosfs,muonisosfunc,elid_pts,elid_etas,elecisosfs,elecisosfunc, lepton_pt, lepton_eta, isEl)")
  jVars.Add("leptonHLTSF", "hltfunc(muonhltcorr,elhlt_pts,elhlt_etas,elechltsfs,elechltuncs,yrstr, lepton_pt, lepton_eta, isEl)")


# ------------------ Results ------------------
rframeVars = VarGroup('restFrameVars')
rframeVars.Add('VLQ_mass', 'rfc.compute_mass(rdfslot_, lepton_pt, lepton_eta, lepton_phi, lepton_mass, gcFatJet_pt, gcFatJet_eta, gcFatJet_phi, gcFatJet_mass, MET_pt, MET_phi)')
rframeVars.Add('VLQ_mass_T', 'VLQ_mass[0]')
rframeVars.Add('VLQ_mass_Tbar', 'VLQ_mass[1]')
rframeVars.Add('VLQ_mass_T_r', 'VLQ_mass[2]')
rframeVars.Add('VLQ_mass_Tbar_r', 'VLQ_mass[3]')
rframeVars.Add('VLQ_mass_ratio', 'VLQ_mass_T/VLQ_mass_Tbar')
rframeVars.Add('VLQ_mass_avg', '(VLQ_mass_T+VLQ_mass_Tbar)*0.5')


# ------------------ ------------------ 


nodeToPlot = a.Apply([gjsonVars, gjsonCuts, lVars, lCuts]) 

# Solution to cleanJets() problem:
#       The analyzer .Apply() calls the analyzer .Define().  This .Define() calls self._collectionOrg.CollectionDefCheck(var, newNode).
#  This method executes this line: if re.search(r"\b" + re.escape(c+'s') + r"\b", action_str) and (c+'s' not in self._builtCollections):
#                                       print ('MAKING %ss for %s'%(c,action_str))
#  Apparently somethings get discarded from this _collectionOrg?
#  Instead force the .Apply() from the ActiveNode because the node .Apply() is better.

newNode = a.ActiveNode.Apply(jVars)
a.SetActiveNode(newNode)

a.Apply([jCuts, metVars, rframeVars])

allColumns = a.GetColumnNames()
columns = [] #allColumns

#i = 0
for col in allColumns:
    #i = i + 1
    #if i > 49: continue
    if col == "run": break # lets just skip all the original branches?

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

#TODO think do we really want to recreate this everytime?  or just create?
a.Snapshot(columns, "out_Tprime.root", "Events", lazy=False, openOption='RECREATE', saveRunChain=False)

myHist1 = a.GetActiveNode().DataFrame.Histo1D(('m_T_lab', 'Mass of T lab', 25, 500, 2000), 'VLQ_mass_T')
myHist2 = a.GetActiveNode().DataFrame.Histo1D(('m_Tbar_lab', 'Mass of Tbar lab', 25, 500, 2000), 'VLQ_mass_Tbar')
myHist1a = a.GetActiveNode().DataFrame.Histo1D(('m_T', 'Mass of T', 25, 500, 2000), 'VLQ_mass_T_r')
myHist2a = a.GetActiveNode().DataFrame.Histo1D(('m_Tbar', 'Mass of Tbar', 25, 500, 2000), 'VLQ_mass_Tbar_r')
myHist3 = a.GetActiveNode().DataFrame.Histo1D(('m_T/m_Tbar', 'Mass ratio of the two particles', 25, 0, 2), 'VLQ_mass_ratio')
myHist4 = a.GetActiveNode().DataFrame.Histo1D(('m_avg', 'Mass average of the two', 25, 500, 2000), 'VLQ_mass_avg')

out = ROOT.TFile.Open('test_Tprime_out.root','RECREATE') #'UPDATE')
myHist1.Write()
myHist2.Write()
myHist1a.Write()
myHist2a.Write()
myHist3.Write()
myHist4.Write()

print("--------- Analysis End ---------")

out.Close()


a.Close()

