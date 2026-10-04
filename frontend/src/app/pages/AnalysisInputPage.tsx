import { useState } from "react";
import { useNavigate } from "react-router";
import { Search, Home, DollarSign, FileText, ChevronRight, ChevronLeft } from "lucide-react";
import { analyzeRisk, AnalysisRequest } from "../services/api";

export function AnalysisInputPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false); // 로딩 상태
  const [error, setError] = useState(""); // 에러 메시지

  const [formData, setFormData] = useState({
    address: "",
    buildingType: "단독",
    area: "",
    landArea: "",
    deposit: "",
    mortgage: "",
    priorTenants: "",
    buildingAge: "",
  });

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    }
  };

  // 백엔드로 분석 요청 보내기
  const handleSubmit = async () => {
    // 로딩 시작
    setLoading(true);
    setError("");

    try {
      // API 요청 데이터 준비
      const requestData: AnalysisRequest = {
        address: formData.address,
        buildingType: formData.buildingType,
        area: formData.area,
        landArea: formData.landArea || "",
        deposit: formData.deposit,
        mortgage: formData.mortgage,
        priorTenants: formData.priorTenants || "0", // 없으면 0
        buildingAge: formData.buildingAge || "",
      };

      // 백엔드로 POST 요청
      const result = await analyzeRisk(requestData);

      // 성공하면 결과 페이지로 이동 (결과 데이터 전달)
      navigate("/results", {
        state: {
          analysisResult: result,
          formData: formData
        }
      });

    } catch (err) {
      // 에러 처리
      console.error("분석 요청 실패:", err);
      setError("분석 요청에 실패했습니다. 다시 시도해주세요.");
    } finally {
      // 로딩 종료
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  return (
    <div className="min-h-screen py-12">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-400'}`}>
              1
            </div>
            <div className={`h-1 flex-1 mx-2 ${step >= 2 ? 'bg-blue-600' : 'bg-slate-200'}`}></div>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-400'}`}>
              2
            </div>
            <div className={`h-1 flex-1 mx-2 ${step >= 3 ? 'bg-blue-600' : 'bg-slate-200'}`}></div>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold ${step >= 3 ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-400'}`}>
              3
            </div>
          </div>
          <div className="flex justify-between text-sm px-1">
            <span className={`font-medium ${step >= 1 ? 'text-blue-600' : 'text-slate-400'}`}>주소 정보</span>
            <span className={`font-medium ${step >= 2 ? 'text-blue-600' : 'text-slate-400'}`}>계약 정보</span>
            <span className={`font-medium ${step >= 3 ? 'text-blue-600' : 'text-slate-400'}`}>권리 정보</span>
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-8">
          {/* Step 1: Address */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-900 mb-2">주소를 입력해주세요</h2>
                <p className="text-slate-600">분석하실 전세 매물의 정확한 주소를 입력해주세요</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  주소 <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    placeholder="예: 용인시 수지구 죽전동 123-456"
                    className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12"
                  />
                  <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                </div>
                <p className="mt-2 text-sm text-slate-500">도로명 주소 또는 지번 주소를 입력하세요</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  건물 유형 <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {["단독", "다가구"].map((type) => (
                    <button
                      key={type}
                      onClick={() => setFormData({ ...formData, buildingType: type })}
                      className={`py-3 px-4 rounded-xl border transition-all ${
                        formData.buildingType === type
                          ? "border-blue-600 bg-blue-50 text-blue-600"
                          : "border-slate-300 hover:border-slate-400"
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  전용면적 (㎡) <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Home className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={formData.area}
                    onChange={(e) => setFormData({ ...formData, area: e.target.value })}
                    placeholder="84.5"
                    className="w-full px-4 py-3 pl-12 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  대지면적 (㎡) <span className="text-slate-400 text-xs font-normal ml-1">(선택)</span>
                </label>
                <div className="relative">
                  <Home className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={formData.landArea}
                    onChange={(e) => setFormData({ ...formData, landArea: e.target.value })}
                    placeholder="120.0"
                    className="w-full px-4 py-3 pl-12 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <p className="mt-2 text-sm text-slate-500">등기부등본 또는 건축물대장에서 확인하세요</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  건축년도 (선택)
                </label>
                <input
                  type="text"
                  value={formData.buildingAge}
                  onChange={(e) => setFormData({ ...formData, buildingAge: e.target.value })}
                  placeholder="2020"
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          )}

          {/* Step 2: Contract */}
          {step === 2 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-900 mb-2">계약 정보를 입력해주세요</h2>
                <p className="text-slate-600">계약서 내용을 바탕으로 입력해주세요</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  보증금 <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={formData.deposit}
                    onChange={(e) => setFormData({ ...formData, deposit: e.target.value })}
                    placeholder="500,000,000"
                    className="w-full px-4 py-3 pl-12 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500">원</span>
                </div>
                <p className="mt-2 text-sm text-slate-500">5억원의 경우 500000000으로 입력하세요</p>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex gap-3">
                  <FileText className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-blue-900 mb-1">전세 계약서를 준비해주세요</h4>
                    <p className="text-sm text-blue-700">
                      다음 단계에서 등기부등본 정보가 필요합니다. 미리 확인해두시면 편리합니다.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Rights */}
          {step === 3 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-slate-900 mb-2">권리 정보를 입력해주세요</h2>
                <p className="text-slate-600">등기부등본을 참고하여 입력해주세요</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  근저당 설정액 <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={formData.mortgage}
                    onChange={(e) => setFormData({ ...formData, mortgage: e.target.value })}
                    placeholder="300,000,000"
                    className="w-full px-4 py-3 pl-12 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500">원</span>
                </div>
                <p className="mt-2 text-sm text-slate-500">모든 근저당의 합계액을 입력하세요</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  선순위 세입자 보증금 총액 (선택)
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={formData.priorTenants}
                    onChange={(e) => setFormData({ ...formData, priorTenants: e.target.value })}
                    placeholder="0"
                    className="w-full px-4 py-3 pl-12 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500">원</span>
                </div>
                <p className="mt-2 text-sm text-slate-500">없으면 0으로 입력하세요</p>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                <div className="flex gap-3">
                  <FileText className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-amber-900 mb-1">등기부등본 확인 방법</h4>
                    <p className="text-sm text-amber-700">
                      대법원 인터넷등기소에서 열람 가능합니다. 근저당권설정 항목의 채권최고액을 모두 더하세요.
                    </p>
                  </div>
                </div>
              </div>

              {/* 에러 메시지 */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              )}
            </div>
          )}

          {/* Navigation */}
          <div className="flex gap-3 mt-8">
            {step > 1 && (
              <button
                onClick={handleBack}
                disabled={loading}
                className="flex items-center gap-2 px-6 py-3 border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors disabled:opacity-50"
              >
                <ChevronLeft className="w-5 h-5" />
                이전
              </button>
            )}
            <button
              onClick={step === 3 ? handleSubmit : handleNext}
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? "분석 중..." : (step === 3 ? "분석 시작하기" : "다음")}
              {!loading && <ChevronRight className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Help */}
      </div>
    </div>
  );
}